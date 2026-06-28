MATCH (n) DETACH DELETE n;

CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;

MERGE (e:Entity {id: "m.malaysia"}) SET e.label = "Malaysia", e.aliases = ["malaysia"], e.description = "Malaysia is a federal constitutional monarchy located in Southeast Asia.";
MERGE (e:Entity {id: "m.malaysia_film"}) SET e.label = "Malaysia", e.aliases = ["malaysia"], e.description = "Malaysia is a fictional travel film entry used in the toy KG to create an ambiguous entity-name example.";
MERGE (e:Entity {id: "m.parliamentary_system"}) SET e.label = "Parliamentary system", e.aliases = ["parliamentary system"], e.description = "A system of democratic governance where the executive derives legitimacy from the legislature.";
MERGE (e:Entity {id: "m.constitutional_monarchy"}) SET e.label = "Constitutional monarchy", e.aliases = ["constitutional monarchy"], e.description = "A monarchy in which the monarch's powers are limited by a constitution.";
MERGE (e:Entity {id: "m.democracy"}) SET e.label = "Democracy", e.aliases = ["democracy"], e.description = "A system of government in which power is vested in the people.";
MERGE (e:Entity {id: "m.elective_monarchy"}) SET e.label = "Elective monarchy", e.aliases = ["elective monarchy"], e.description = "A monarchy in which the monarch is elected.";
MERGE (e:Entity {id: "m.kuala_lumpur"}) SET e.label = "Kuala Lumpur", e.aliases = ["kuala lumpur"], e.description = "The capital city of Malaysia.";
MERGE (e:Entity {id: "m.southeast_asia"}) SET e.label = "Southeast Asia", e.aliases = ["southeast asia"], e.description = "A geographic region in Asia.";

MATCH (s:Entity {id: "m.malaysia"}), (o:Entity {id: "m.parliamentary_system"}) MERGE (s)-[r:LOCATION_COUNTRY_FORM_OF_GOVERNMENT {predicate: "location.country.form_of_government"}]->(o);
MATCH (s:Entity {id: "m.malaysia"}), (o:Entity {id: "m.constitutional_monarchy"}) MERGE (s)-[r:LOCATION_COUNTRY_FORM_OF_GOVERNMENT {predicate: "location.country.form_of_government"}]->(o);
MATCH (s:Entity {id: "m.malaysia"}), (o:Entity {id: "m.democracy"}) MERGE (s)-[r:LOCATION_COUNTRY_FORM_OF_GOVERNMENT {predicate: "location.country.form_of_government"}]->(o);
MATCH (s:Entity {id: "m.malaysia"}), (o:Entity {id: "m.elective_monarchy"}) MERGE (s)-[r:LOCATION_COUNTRY_FORM_OF_GOVERNMENT {predicate: "location.country.form_of_government"}]->(o);
MATCH (s:Entity {id: "m.malaysia"}), (o:Entity {id: "m.kuala_lumpur"}) MERGE (s)-[r:LOCATION_COUNTRY_CAPITAL {predicate: "location.country.capital"}]->(o);
MATCH (s:Entity {id: "m.malaysia"}), (o:Entity {id: "m.southeast_asia"}) MERGE (s)-[r:LOCATION_LOCATION_CONTAINEDBY {predicate: "location.location.containedby"}]->(o);

MATCH (n)-[r]->(m) RETURN n, r, m;
