# Dataset metadata

`data/processed/dataset_metadata.ttl` describes the dataset itself, using three standard vocabularies:

| Concern | Vocabulary | What is described |
|---|---|---|
| Discovery / description | **DCAT** + Dublin Core Terms | `dcat:Catalog`, `dcat:Dataset` (title EN/VI, description, keywords, issued/modified), one `dcat:Distribution` per Turtle file with download URL and size |
| Content statistics / links | **VoID** | triples, entities, class and property partitions, vocabularies, URI space, `void:Linkset` for the Wikidata and DBpedia `owl:sameAs` links |
| Provenance | **PROV-O** | the dataset `prov:wasDerivedFrom` the two Kaggle CSVs and `prov:wasGeneratedBy` one pipeline `prov:Activity` that `prov:used` the Kaggle files, Wikidata, DBpedia and our four scripts |
| License | `dcterms:license`, `dcterms:rights` | on the dataset, every distribution and every linkset |

The dataset resource is also typed `void:Dataset`, so VoID and DCAT consumers see the same node.

## Regenerate

Statistics are computed from the real files, so re-run after any change to the data:

```bash
python scripts/generate_metadata.py          # writes data/processed/dataset_metadata.ttl
```

The script stops with an error if the `owl:sameAs` counts in the TTL files differ from
`link_report.csv`. `dcterms:created` is kept from the previous file; `dcterms:modified` is updated.

## Pipeline described by the provenance

```
TMDB 5000 CSVs (Kaggle)
  -- prepare_movies_csv.py --> data/raw/movies.csv
  -- csv_to_rdf.py         --> data/processed/movies.ttl
  -- link_wikidata_dbpedia.py (uses Wikidata, DBpedia) --> movies_linked.ttl + link_report.csv
  -- add_awards.py         --> awards.ttl
```

The metadata models this as a single activity (`meta:pipeline`) rather than one
activity per script.

## Licensing

| Part | License |
|---|---|
| Code (`scripts/`) | MIT (`LICENSE`) |
| Our RDF data and metadata | CC BY-NC 4.0 |
| Upstream movie facts | TMDb API terms of use |
| Wikidata links | CC0 |
| DBpedia links | CC BY-SA |

Note: the TMDb terms restrict redistribution and commercial use, so the derived RDF is
published as non-commercial with attribution. The group should confirm this choice;
to change it, edit `DATASET_LICENSE` in `scripts/generate_metadata.py` and regenerate.

## Example queries

```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX void: <http://rdfs.org/ns/void#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>

# Title, license and size
SELECT ?title ?license ?triples WHERE {
  ?d a dcat:Dataset, void:Dataset ; dcterms:title ?title ; dcterms:license ?license ; void:triples ?triples .
  FILTER(lang(?title) = "en")
}

# Links per target dataset
SELECT ?linkset ?n WHERE { ?linkset a void:Linkset ; void:triples ?n }
```
