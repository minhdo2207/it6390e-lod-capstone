# Project Plan — Movies LOD Knowledge Graph

## 1. Domain

Movies: films, directors, actors, genres, studios, countries. Chosen because there
is a large amount of open reference data available (TMDB, DBpedia, Wikidata),
which makes reaching the 5-star level realistic within the project timeline.

## 2. Competency questions

- Who directed movie X?
- Which movies feature actor Y?
- Which movies belong to genre G and were released after year Y?
- Which director has the most movies in the dataset?
- Which movies are related to movie X (same director / same cast)?

## 3. Ontology sketch

Classes:

| Class | Notes |
|---|---|
| `Movie` | reuse `schema:Movie` |
| `Person` | reuse `foaf:Person` |
| `Director` | subclass of `Person` |
| `Actor` | subclass of `Person` |
| `Genre` | |
| `Studio` | |
| `Country` | |

Properties (prefer reusing existing vocabulary terms before minting new ones):

| Property | Domain -> Range | Source |
|---|---|---|
| `dbo:director` | Movie -> Director | DBpedia ontology |
| `dbo:starring` | Movie -> Actor | DBpedia ontology |
| `hasGenre` | Movie -> Genre | local |
| `dc:title` | Movie -> literal | Dublin Core |
| `schema:datePublished` | Movie -> literal | schema.org |
| `producedBy` | Movie -> Studio | local |
| `producedIn` | Movie -> Country | local |
| `foaf:name` | Person -> literal | FOAF |

## 4. Data collection

Source: TMDB / Kaggle movie dataset (open license). Scope limited to ~150-300
movies to keep the ontology + linking work manageable within the timeline.

## 5. 4-star: CSV -> RDF

`scripts/csv_to_rdf.py` reads the raw CSV, mints a URI per movie/person, and
serializes the result as Turtle.

## 6. 5-star: linking

`scripts/link_dbpedia.py` looks up each movie (by title + year, to avoid
false positives on remakes/sequels) on DBpedia and Wikidata and adds
`owl:sameAs` links when a confident match is found. Ambiguous matches are
left unlinked rather than guessed.

## 7. SPARQL endpoint

Load `data/processed/movies_linked.ttl` into Apache Jena Fuseki for the demo.
Sample queries live in `sparql/sample_queries.rq`.

## 8. Timeline

| Date | Task |
|---|---|
| Day 1-2 | Finalize scope, competency questions, ontology sketch |
| Day 3-4 | Collect and clean data |
| Day 5-6 | CSV -> RDF pipeline (4-star) |
| Day 7 | Linking to DBpedia/Wikidata (5-star) |
| Day 8 | SPARQL endpoint + queries |
| Day 9 | Report, slides, demo video |
| Day 10 | Presentation |
