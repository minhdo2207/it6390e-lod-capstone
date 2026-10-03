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
Kaggle TMDB 5000 CSVs  -->  scripts/prepare_movies_csv.py  -->  data/raw/movies.csv
                                                                      |
                                              +-----------------------+
                                              v
              scripts/csv_to_rdf.py  -->  data/processed/movies.ttl
                                              |
                                              v
                               scripts/link_wikidata_dbpedia.py
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

# Source data: download "TMDB 5000 Movie Dataset" from
# https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata and unzip it into data/raw/
python scripts/prepare_movies_csv.py data/raw/tmdb_5000_movies.csv data/raw/tmdb_5000_credits.csv data/raw/movies.csv

python scripts/csv_to_rdf.py data/raw/movies.csv data/processed/movies.ttl
python scripts/link_wikidata_dbpedia.py data/processed/movies.ttl data/processed/movies_linked.ttl data/processed/link_report.csv
```

`link_report.csv` lists every movie and person with the Wikidata / DBpedia
links found, for manual review.

Awards (for the `AwardWinningDirector` class):

```bash
python scripts/add_awards.py data/processed/link_report.csv data/processed/awards.ttl
```

Then load `ontology/movies.ttl`, `data/processed/movies_linked.ttl` and
`data/processed/awards.ttl` into Protege (or a triple store such as Apache Jena
Fuseki) and query it using the examples in `sparql/sample_queries.rq`.

## Reasoning check

Runs HermiT over the ontology and data without opening Protege (needs Java):

```bash
pip install owlready2
python scripts/check_reasoning.py --demo
```

Expected: 29 `ActionMovie`, 16 `ComedyMovie`, 32 `AwardWinningDirector`,
5 `ActorDirector` (from the SWRL rule), and an inconsistency once
`ontology/demo_inconsistency.ttl` is added. Demo steps for Protege are in
`docs/DEMO_SCRIPT.md`.

## Team

Group 2 — IT6390E, HUST.

## License

Data is redistributed under the same open license as its source dataset.
Code in this repo is released under the MIT License.
