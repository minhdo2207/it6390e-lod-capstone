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

The queries are in `sparql/sample_queries.rq` (1-5), `sparql/federated_queries.rq`
(6-15) and `sparql/castrole_queries.rq` (16-21).

### Cast roles (n-ary relation)

`dbo:starring` only says that an actor is in a movie, so there is nowhere to put
the character played or the billing position. Following the W3C note
*Defining N-ary Relations*, each appearance of an actor in a movie is a node of
its own, `ont:CastRole`:

```
movie --ont:hasCastRole--> role --ont:playedBy--> actor
role --ont:characterName--> "Bruce Wayne"       role --ont:billingOrder--> 1
role --ont:roleInMovie--> movie                 (inverse of hasCastRole)
```

```turtle
ex:role/155-3894 a ont:CastRole ;
    rdfs:label "Christian Bale as Bruce Wayne in The Dark Knight"@en ;
    ont:playedBy ex:person/3894 ;
    ont:roleInMovie ex:movie/155 ;
    ont:characterName "Bruce Wayne" ;
    ont:billingOrder 1 .
```

- `dbo:starring` is kept because existing data and queries use it. The ontology
  declares `hasCastRole o playedBy` as a property chain implying `dbo:starring`,
  and the data states both, so they never disagree:
  `python scripts/check_reasoning.py` checks that the two give the same
  movie-actor pairs, and query 21 does the same in SPARQL.
- `billingOrder` is the position in the credits (1 = top-billed). Only the 3
  first-billed actors of each movie are in the data, so there are 750 roles.
- `characterName` is a plain string taken from TMDB, not a resource: the same
  name can be different characters (query 18 shows "Sam" played by three actors
  in three movies), and linking characters would need identity resolution that
  the source does not provide.
- Role URIs are `ex:role/<movie id>-<actor id>`. The roles are produced by
  `scripts/csv_to_rdf.py` from the `cast_characters` column of the raw CSV, so
  they are in `movies.ttl` and `movies_linked.ttl`; the linking step ignores them
  (it only links `schema:Movie` and `foaf:Person`).

### Federated queries (Wikidata / DBpedia)

`sparql/federated_queries.rq` (queries 6-10) joins our data with Wikidata and
DBpedia through `SERVICE`, using the `owl:sameAs` links from the linking step.
They need internet access:

```bash
python scripts/sparql_cli.py -n 7   #run query #7
```

Add `-v` (for example `python scripts/sparql_cli.py -n 13 -v`) to print every
request sent to Wikidata/DBpedia and how many rows came back; the request can
be pasted into <https://dbpedia.org/sparql> to see the raw answer. The CLI also
prints a warning when the endpoint says its answer is incomplete (query
timeout).

## Dataset metadata

`data/processed/dataset_metadata.ttl` describes the dataset itself (LOD best
practices on metadata, licensing and provenance):

- **VoID**: a `void:Dataset` with title, description, `dcterms:license`,
  `dcterms:source` (Kaggle TMDB 5000, Wikidata, DBpedia), `dcterms:created` and
  `void:triples`, plus two `void:Linkset`s (`owl:sameAs` to Wikidata: 920 links,
  to DBpedia: 912 links). The dataset is also typed `dcat:Dataset`, with one
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


## Reasoning check

Runs HermiT over the ontology and data without opening Protege (needs Java):

```bash
pip install owlready2
python scripts/check_reasoning.py --demo
```

Expected: 29 `ActionMovie`, 16 `ComedyMovie`, 32 `AwardWinningDirector`,
5 `ActorDirector` (from the SWRL rule), and an inconsistency once
`ontology/demo_inconsistency.ttl` is added.

## Team

Group 2 — IT6390E, HUST.

## License

Code in this repo is released under the MIT License (see `LICENSE`).

The generated RDF data and its metadata are proposed under CC BY-NC 4.0.

Movie data comes from the Kaggle "TMDB 5000 Movie Dataset", which is built from
the TMDb API. This product uses the TMDb API but is not endorsed or certified
by TMDb. Wikidata content is CC0; DBpedia content is CC BY-SA.
