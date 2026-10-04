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
    └── processed/  generated RDF/Turtle output, incl. dataset_metadata.ttl
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
                                    scripts/sparql_cli.py  /  Protege SPARQL tab
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
`data/processed/awards.ttl` into Protege, or query from the terminal:

```bash
python scripts/sparql_cli.py          # interactive prompt (:list, :3, :quit)
python scripts/sparql_cli.py -n 3     # run sample query #3
```

The queries are in `sparql/sample_queries.rq`.

## Dataset metadata

`data/processed/dataset_metadata.ttl` describes the dataset itself (LOD best
practices on metadata, licensing and provenance):

- **VoID**: a `void:Dataset` with title, description, `dcterms:license`,
  `dcterms:source` (Kaggle TMDB 5000, Wikidata, DBpedia), `dcterms:created` and
  `void:triples`, plus two `void:Linkset`s (`owl:sameAs` to Wikidata: 920 links,
  to DBpedia: 916 links). The dataset is also typed `dcat:Dataset`, with one
  `dcat:Distribution` per Turtle file.
- **PROV-O**: the dataset `prov:wasDerivedFrom` the Kaggle CSV files and
  `prov:wasGeneratedBy` a pipeline activity that `prov:used` our scripts.

The counts are computed from the data files (and checked against
`link_report.csv`), so regenerate the file after changing the data:

```bash
python scripts/generate_metadata.py
```

Check that it parses:

```bash
python -c "from rdflib import Graph; Graph().parse('data/processed/dataset_metadata.ttl')"
```

Details and example queries are in `docs/METADATA.md`.

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

Code in this repo is released under the MIT License (see `LICENSE`).

The generated RDF data and its metadata are proposed under CC BY-NC 4.0 (see
`docs/METADATA.md`).

Movie data comes from the Kaggle "TMDB 5000 Movie Dataset", which is built from
the TMDb API. This product uses the TMDb API but is not endorsed or certified
by TMDb. Wikidata content is CC0; DBpedia content is CC BY-SA.
