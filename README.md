# IT6390E — Linked Open Data Capstone: Movies Knowledge Graph

Capstone project for **IT6390E - Knowledge Graphs** (HUST). Group 2.

## Goal

Build a Linked Open Data (LOD) application for the **movies** domain, following the
5-star Linked Data deployment scheme:

1. Define an ontology for the movie domain
2. Collect movie data (title, year, director, cast, genre, studio, country)
3. Transform the data into RDF (4-star: RDF + URIs, non-proprietary format)
4. Link entities to DBpedia / Wikidata (5-star)
5. Expose the data through a SPARQL endpoint

## Repo structure

```
.
├── docs/           project plan, ontology design notes
├── ontology/       OWL/Turtle ontology definitions
├── scripts/        data pipeline (CSV -> RDF, linking to DBpedia/Wikidata)
├── sparql/         sample SPARQL queries used for the demo
└── data/
    ├── raw/        original source data (CSV)
    └── processed/  generated RDF/Turtle output
```

## Pipeline

```
raw CSV  -->  scripts/csv_to_rdf.py  -->  data/processed/movies.ttl
                                              |
                                              v
                                   scripts/link_dbpedia.py
                                              |
                                              v
                                   data/processed/movies_linked.ttl
                                              |
                                              v
                                    load into Fuseki -> SPARQL endpoint
```

## Running locally

```bash
pip install -r requirements.txt
python scripts/csv_to_rdf.py data/raw/movies.csv data/processed/movies.ttl
python scripts/link_dbpedia.py data/processed/movies.ttl data/processed/movies_linked.ttl
```

Then load `data/processed/movies_linked.ttl` into a triple store (e.g. Apache Jena
Fuseki) and query it using the examples in `sparql/sample_queries.rq`.

## Team

Group 2 — IT6390E, HUST.

## License

Data is redistributed under the same open license as its source dataset.
Code in this repo is released under the MIT License.
