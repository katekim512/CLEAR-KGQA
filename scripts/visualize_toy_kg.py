import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KG_PATH = ROOT / "data" / "mock_kg" / "freebase_toy.json"
OUT_DIR = ROOT / "docs"


def node_id(entity_id):
    return re.sub(r"[^A-Za-z0-9_]", "_", entity_id)


def escape_label(text):
    return text.replace('"', '\\"')


def main():
    kg = json.loads(KG_PATH.read_text(encoding="utf-8"))
    entities = {entity["id"]: entity for entity in kg["entities"]}

    lines = ["flowchart LR"]
    for entity in kg["entities"]:
        nid = node_id(entity["id"])
        label = escape_label(entity["label"])
        if entity["label"] == "Malaysia":
            label = f"{label}<br/>{escape_label(entity['description'][:58])}..."
        lines.append(f'  {nid}["{label}"]')

    for triple in kg["triples"]:
        source = node_id(triple["subject"])
        target = node_id(triple["object"])
        predicate = escape_label(triple["predicate"])
        lines.append(f'  {source} -->|"{predicate}"| {target}')

    mermaid = "\n".join(lines) + "\n"
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "toy_kg_graph.mmd").write_text(mermaid, encoding="utf-8")
    (OUT_DIR / "toy_kg_graph.md").write_text(
        "# Toy KG Graph\n\n```mermaid\n" + mermaid + "```\n",
        encoding="utf-8",
    )

    print(f"Entities: {len(entities)}")
    print(f"Triples: {len(kg['triples'])}")
    print(f"Wrote {OUT_DIR / 'toy_kg_graph.mmd'}")
    print(f"Wrote {OUT_DIR / 'toy_kg_graph.md'}")


if __name__ == "__main__":
    main()
