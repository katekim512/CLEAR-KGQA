import json
import re
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import FastAPI, Request


app = FastAPI(title="CLEAR-KGQA Mock Freebase Backend")

KG_PATH = Path(__file__).parent / "data" / "mock_kg" / "freebase_toy.json"


def load_kg():
    with KG_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    entities = {entity["id"]: entity for entity in data["entities"]}
    return entities, data["triples"]


ENTITIES, TRIPLES = load_kg()


def entity_label(entity_id):
    return ENTITIES[entity_id]["label"]


def entity_description(entity_id):
    return ENTITIES[entity_id].get("description", "No description.")


def normalize(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def token_score(query, text):
    query_tokens = set(normalize(query).split())
    text_tokens = set(normalize(text).split())
    if not query_tokens:
        return 0
    return len(query_tokens & text_tokens)


def find_entities(query):
    scored = []
    for entity_id, entity in ENTITIES.items():
        haystack = " ".join(
            [entity["label"], entity.get("description", ""), *entity.get("aliases", [])]
        )
        score = token_score(query, haystack)
        if normalize(query) and normalize(query) in normalize(haystack):
            score += 10
        if score > 0:
            scored.append((score, entity_id))
    scored.sort(reverse=True)
    return [entity_id for _, entity_id in scored]


def parse_bool(value):
    return str(value).lower() in {"1", "true", "yes"}


def format_entity_search_results(entity_ids):
    grouped = {}
    ordered_labels = []
    for entity_id in entity_ids:
        label = entity_label(entity_id)
        if label not in grouped:
            grouped[label] = []
            ordered_labels.append(label)
        grouped[label].append(entity_id)

    results = []
    for label in ordered_labels:
        descs = [f"Description: {entity_description(entity_id)}" for entity_id in grouped[label]]
        results.append(f'"{label}" | ' + " | ".join(descs))
    return results


def format_entity_search_structured(entity_ids):
    grouped = {}
    for rank, entity_id in enumerate(entity_ids):
        label = entity_label(entity_id)
        grouped.setdefault(label, []).append(
            {
                "mid": entity_id,
                "score": 100 - rank,
                "desc": entity_description(entity_id),
            }
        )
    return grouped


def entity_ids_mentioned(text):
    text_l = text.lower()
    found = []
    for entity_id, entity in ENTITIES.items():
        names = [entity["label"], *entity.get("aliases", [])]
        if any(name.lower() in text_l for name in names):
            found.append(entity_id)
    return found


def predicate_score(predicate, semantic):
    words = predicate.replace(".", " ").replace("_", " ")
    score = token_score(semantic, words)
    if "government" in normalize(semantic) and "government" in words:
        score += 3
    if "capital" in normalize(semantic) and "capital" in words:
        score += 3
    return score


def matching_triples_for_patterns(sparql, semantic):
    mentioned = entity_ids_mentioned(sparql)
    candidates = []
    for triple in TRIPLES:
        if mentioned and triple["subject"] not in mentioned and triple["object"] not in mentioned:
            continue
        score = predicate_score(triple["predicate"], semantic)
        if not semantic:
            score = 1
        if score > 0:
            candidates.append((score, triple))
    candidates.sort(key=lambda item: item[0], reverse=True)
    return [triple for _, triple in candidates]


def format_triple_pattern(triple):
    subject = entity_label(triple["subject"])
    obj = entity_label(triple["object"])
    return f'("{subject}", {triple["predicate"]}, "{obj}")'


def execute_simple_sparql(sparql):
    sparql_l = sparql.lower()
    mentioned = entity_ids_mentioned(sparql)
    predicates = {
        triple["predicate"]
        for triple in TRIPLES
        if triple["predicate"].lower() in sparql_l
    }
    if not mentioned or not predicates:
        return ["_None"]

    answers = []
    for triple in TRIPLES:
        if triple["predicate"] not in predicates:
            continue
        if triple["subject"] in mentioned:
            answers.append(entity_label(triple["object"]))
        elif triple["object"] in mentioned:
            answers.append(entity_label(triple["subject"]))

    return sorted(set(answers)) if answers else ["_None"]


async def read_form(request: Request):
    body = (await request.body()).decode("utf-8")
    parsed = parse_qs(body)
    return {key: values[-1] if values else "" for key, values in parsed.items()}


@app.get("/fb/test")
def test():
    return {
        "status": "ok",
        "backend": "toy-freebase",
        "entities": len(ENTITIES),
        "triples": len(TRIPLES),
    }


@app.post("/fb/SearchNodes")
async def search_nodes(request: Request):
    form = await read_form(request)
    query = form.get("query", "")
    n_results = int(form.get("n_results", 10))
    str_mode = parse_bool(form.get("str_mode", True))
    entity_ids = find_entities(query)
    if not str_mode:
        return format_entity_search_structured(entity_ids[:n_results])

    results = format_entity_search_results(entity_ids)
    if not results:
        results = [f'"{query}" | No description.']
    return results[:n_results]


@app.post("/fb/SearchGraphPatterns")
async def search_graph_patterns(request: Request):
    form = await read_form(request)
    sparql = form.get("sparql", "")
    semantic = form.get("semantic", "")
    topN_return = int(form.get("topN_return", 10))
    results = [
        format_triple_pattern(triple)
        for triple in matching_triples_for_patterns(sparql, semantic)
    ]
    if not results:
        results = ['(?e, type.object.name, "Mock result")']
    return results[:topN_return]


@app.post("/fb/ExecuteSPARQL")
async def execute_sparql(request: Request):
    form = await read_form(request)
    sparql = form.get("sparql", "")
    return execute_simple_sparql(sparql)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=19901)
