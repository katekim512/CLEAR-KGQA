import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KG_PATH = ROOT / "data" / "mock_kg" / "freebase_toy.json"
OUT_PATH = ROOT / "docs" / "toy_kg_import.cypher"


def cypher_string(value):
    return json.dumps(value, ensure_ascii=False)


def rel_type(predicate):
    return predicate.upper().replace(".", "_").replace("-", "_")


def main():
    kg = json.loads(KG_PATH.read_text(encoding="utf-8"))
    lines = [
        "MATCH (n) DETACH DELETE n;",
        "",
        "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;",
        "",
    ]

    for entity in kg["entities"]:
        aliases = "[" + ", ".join(cypher_string(alias) for alias in entity.get("aliases", [])) + "]"
        lines.append(
            "MERGE (e:Entity {id: "
            + cypher_string(entity["id"])
            + "}) "
            + "SET e.label = "
            + cypher_string(entity["label"])
            + ", e.aliases = "
            + aliases
            + ", e.description = "
            + cypher_string(entity.get("description", ""))
            + ";"
        )

    lines.append("")
    for triple in kg["triples"]:
        lines.append(
            "MATCH (s:Entity {id: "
            + cypher_string(triple["subject"])
            + "}), (o:Entity {id: "
            + cypher_string(triple["object"])
            + "}) "
            + "MERGE (s)-[r:"
            + rel_type(triple["predicate"])
            + " {predicate: "
            + cypher_string(triple["predicate"])
            + "}]->(o);"
        )

    lines.extend(
        [
            "",
            "MATCH (n)-[r]->(m) RETURN n, r, m;",
        ]
    )

    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
