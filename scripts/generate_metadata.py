"""Generate dataset-level metadata (VoID + DCAT + PROV-O + license) as Turtle.

Usage:
    python generate_metadata.py [output.ttl]

Default output: data/processed/dataset_metadata.ttl

Triple counts and link counts are computed from the actual files in
data/processed/ (and cross-checked against link_report.csv), so re-run this
script after regenerating the data to keep the metadata in sync.
"""

import csv
import sys
from datetime import date
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef, XSD
from rdflib.namespace import DCAT, DCTERMS, FOAF, PROV, VOID

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "data" / "processed" / "dataset_metadata.ttl"

BASE = "http://it6390e-group2.example.org/"
META = Namespace(BASE + "metadata/")
RES = BASE + "resource/"

# Files that make up the published dataset (the ontology is a separate artifact).
DATA_FILES = {
    "movies_linked": ROOT / "data/processed/movies_linked.ttl",
    "awards": ROOT / "data/processed/awards.ttl",
}
ONTOLOGY_FILE = ROOT / "ontology/movies.ttl"
LINK_REPORT = ROOT / "data/processed/link_report.csv"
SCRIPTS = [
    "prepare_movies_csv.py",
    "csv_to_rdf.py",
    "link_wikidata_dbpedia.py",
    "add_awards.py",
]

REPO = URIRef("https://github.com/minhdo2207/it6390e-lod-capstone")
RAW = "https://raw.githubusercontent.com/minhdo2207/it6390e-lod-capstone/main/"
KAGGLE = URIRef("https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata")
WIKIDATA = URIRef("https://www.wikidata.org/")
DBPEDIA = URIRef("https://dbpedia.org/")

# License of the derived RDF. TMDb's terms restrict redistribution and
# commercial use, so we publish as non-commercial with attribution.
DATASET_LICENSE = URIRef("https://creativecommons.org/licenses/by-nc/4.0/")
LICENSES = {
    DATASET_LICENSE: "Creative Commons Attribution-NonCommercial 4.0",
    URIRef("https://opensource.org/licenses/MIT"): "MIT License",
    URIRef("https://creativecommons.org/publicdomain/zero/1.0/"): "Creative Commons CC0 1.0 Universal",
    URIRef("https://creativecommons.org/licenses/by-sa/3.0/"): "Creative Commons Attribution-ShareAlike 3.0",
    URIRef("https://www.themoviedb.org/api-terms-of-use"): "TMDb API Terms of Use",
}
TMDB_TERMS = URIRef("https://www.themoviedb.org/api-terms-of-use")
CC0 = URIRef("https://creativecommons.org/publicdomain/zero/1.0/")
CC_BY_SA = URIRef("https://creativecommons.org/licenses/by-sa/3.0/")
MIT = URIRef("https://opensource.org/licenses/MIT")

SCHEMA_MOVIE = URIRef("http://schema.org/Movie")
INT = XSD.integer


def load(path):
    g = Graph()
    g.parse(path, format="turtle")
    return g


def count_links(g):
    """Count owl:sameAs statements per target dataset."""
    links = {"wikidata": 0, "dbpedia": 0}
    for o in g.objects(None, OWL.sameAs):
        if str(o).startswith("http://www.wikidata.org/"):
            links["wikidata"] += 1
        elif str(o).startswith("http://dbpedia.org/"):
            links["dbpedia"] += 1
    return links


def stats(g):
    classes, props = {}, {}
    for s, p, o in g:
        props[p] = props.get(p, 0) + 1
        if p == RDF.type:
            classes.setdefault(o, set()).add(s)
    return {
        "triples": len(g),
        "subjects": len(set(g.subjects())),
        "entities": len({s for s in g.subjects() if str(s).startswith(BASE)}),
        "classes": {c: len(ents) for c, ents in classes.items()},
        "properties": props,
        "links": count_links(g),
    }


def report_links():
    """Link counts according to link_report.csv (used as a consistency check)."""
    with open(LINK_REPORT, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return {
        "wikidata": sum(1 for r in rows if r["wikidata"]),
        "dbpedia": sum(1 for r in rows if r["dbpedia"]),
    }


def build(per_file, ont_triples, movie_count, previous_created=None):
    g = Graph()
    for prefix, ns in [("void", VOID), ("dcterms", DCTERMS), ("prov", PROV), ("dcat", DCAT),
                       ("foaf", FOAF), ("owl", OWL), ("rdfs", RDFS), ("xsd", XSD),
                       ("meta", META)]:
        g.bind(prefix, ns, override=True)

    today = Literal(date.today().isoformat(), datatype=XSD.date)
    created = previous_created or today

    merged_classes, merged_props = {}, {}
    links = {"wikidata": 0, "dbpedia": 0}
    for s in per_file.values():
        for key, n in s["classes"].items():
            merged_classes[key] = merged_classes.get(key, 0) + n
        for key, n in s["properties"].items():
            merged_props[key] = merged_props.get(key, 0) + n
        for key in links:
            links[key] += s["links"][key]
    total = sum(s["triples"] for s in per_file.values())

    # ---- licenses and agent
    for uri, title in LICENSES.items():
        g.add((uri, RDF.type, DCTERMS.LicenseDocument))
        g.add((uri, DCTERMS.title, Literal(title, lang="en")))
    group = META["group2"]
    g.add((group, RDF.type, PROV.Agent))
    g.add((group, RDF.type, FOAF.Group))
    g.add((group, FOAF.name, Literal("IT6390E Group 2, HUST")))

    # ---- sources (dcterms:source targets)
    for uri, title, lic, desc in [
        (KAGGLE, "TMDB 5000 Movie Dataset (Kaggle)", TMDB_TERMS,
         "tmdb_5000_movies.csv and tmdb_5000_credits.csv, built from the TMDb API."),
        (WIKIDATA, "Wikidata", CC0,
         "Target of owl:sameAs links, found through TMDB id properties P4947 (film) and P4985 (person)."),
        (DBPEDIA, "DBpedia", CC_BY_SA,
         "Target of owl:sameAs links, found through DBpedia's own links to Wikidata items."),
    ]:
        g.add((uri, RDF.type, DCAT.Dataset))
        g.add((uri, RDF.type, PROV.Entity))
        g.add((uri, DCTERMS.title, Literal(title, lang="en")))
        g.add((uri, DCTERMS.description, Literal(desc, lang="en")))
        g.add((uri, DCTERMS.license, lic))
    g.add((WIKIDATA, VOID.uriSpace, Literal("http://www.wikidata.org/entity/")))
    g.add((DBPEDIA, VOID.uriSpace, Literal("http://dbpedia.org/resource/")))

    # ---- the dataset (void:Dataset, also dcat:Dataset)
    dataset = META["dataset"]
    g.add((dataset, RDF.type, VOID.Dataset))
    g.add((dataset, RDF.type, DCAT.Dataset))
    g.add((dataset, RDF.type, PROV.Entity))
    g.add((dataset, DCTERMS.title, Literal("Movies Knowledge Graph (TMDB 5000 subset)", lang="en")))
    g.add((dataset, DCTERMS.title, Literal("Đồ thị tri thức phim (tập con TMDB 5000)", lang="vi")))
    g.add((dataset, DCTERMS.description, Literal(
        f"RDF description of {movie_count} movies with their directors, cast, genre, studio and "
        "country, linked to Wikidata and DBpedia via owl:sameAs. Built for the IT6390E Knowledge "
        "Graphs capstone at HUST.", lang="en")))
    g.add((dataset, DCTERMS.description, Literal(
        f"Mô tả RDF của {movie_count} bộ phim cùng đạo diễn, diễn viên, thể loại, hãng phim và "
        "quốc gia, được liên kết tới Wikidata và DBpedia bằng owl:sameAs. Thực hiện cho đồ án "
        "môn IT6390E Knowledge Graphs, ĐHBK Hà Nội.", lang="vi")))
    g.add((dataset, DCTERMS.license, DATASET_LICENSE))
    g.add((dataset, DCTERMS.rights, Literal(
        "Derived from the TMDb API via the Kaggle TMDB 5000 Movie Dataset. This product uses the "
        "TMDb API but is not endorsed or certified by TMDb. owl:sameAs links point to Wikidata "
        "(CC0) and DBpedia (CC BY-SA).", lang="en")))
    for src in (KAGGLE, WIKIDATA, DBPEDIA):
        g.add((dataset, DCTERMS.source, src))
    g.add((dataset, DCTERMS.creator, group))
    g.add((dataset, DCTERMS.publisher, group))
    g.add((dataset, DCTERMS.created, created))
    g.add((dataset, DCTERMS.modified, today))
    g.add((dataset, DCTERMS.language, URIRef("http://id.loc.gov/vocabulary/iso639-1/en")))
    g.add((dataset, DCAT.landingPage, REPO))
    for kw in ("movies", "linked data", "knowledge graph", "RDF", "DBpedia", "Wikidata"):
        g.add((dataset, DCAT.keyword, Literal(kw, lang="en")))

    # VoID statistics
    g.add((dataset, VOID.triples, Literal(total, datatype=INT)))
    g.add((dataset, VOID.entities,
           Literal(sum(s["entities"] for s in per_file.values()), datatype=INT)))
    g.add((dataset, VOID.distinctSubjects,
           Literal(sum(s["subjects"] for s in per_file.values()), datatype=INT)))
    g.add((dataset, VOID.classes, Literal(len(merged_classes), datatype=INT)))
    g.add((dataset, VOID.properties, Literal(len(merged_props), datatype=INT)))
    g.add((dataset, VOID.uriSpace, Literal(RES)))
    g.add((dataset, VOID.vocabulary, URIRef(BASE + "ontology/")))
    for vocab in ("http://xmlns.com/foaf/0.1/", "http://schema.org/",
                  "http://dbpedia.org/ontology/", "http://purl.org/dc/elements/1.1/"):
        g.add((dataset, VOID.vocabulary, URIRef(vocab)))
    g.add((dataset, VOID.feature, URIRef("http://www.w3.org/ns/formats/Turtle")))
    g.add((dataset, VOID.exampleResource, URIRef(RES + "movie/100")))
    for cls, n in sorted(merged_classes.items(), key=lambda x: str(x[0])):
        part = BNode()
        g.add((dataset, VOID.classPartition, part))
        g.add((part, VOID["class"], cls))
        g.add((part, VOID.entities, Literal(n, datatype=INT)))
    for prop, n in sorted(merged_props.items(), key=lambda x: str(x[0])):
        part = BNode()
        g.add((dataset, VOID.propertyPartition, part))
        g.add((part, VOID.property, prop))
        g.add((part, VOID.triples, Literal(n, datatype=INT)))

    # ---- linksets
    for key, target, label in [("wikidata", WIKIDATA, "Wikidata"), ("dbpedia", DBPEDIA, "DBpedia")]:
        ls = META[f"linkset_{key}"]
        g.add((ls, RDF.type, VOID.Linkset))
        g.add((ls, DCTERMS.title, Literal(f"owl:sameAs links to {label}", lang="en")))
        g.add((ls, VOID.linkPredicate, OWL.sameAs))
        g.add((ls, VOID.subjectsTarget, dataset))
        g.add((ls, VOID.objectsTarget, target))
        g.add((ls, VOID.target, dataset))
        g.add((ls, VOID.target, target))
        g.add((ls, VOID.triples, Literal(links[key], datatype=INT)))
        g.add((ls, DCTERMS.license, DATASET_LICENSE))
        g.add((ls, PROV.wasGeneratedBy, META["pipeline"]))
        g.add((dataset, VOID.subset, ls))

    # ---- distributions
    for key, path in DATA_FILES.items():
        dist = META[f"distribution_{key}"]
        rel = path.relative_to(ROOT).as_posix()
        g.add((dataset, DCAT.distribution, dist))
        g.add((dist, RDF.type, DCAT.Distribution))
        g.add((dist, DCTERMS.title, Literal(path.name)))
        g.add((dist, DCTERMS.format, Literal("text/turtle")))
        g.add((dist, DCAT.mediaType, URIRef("https://www.iana.org/assignments/media-types/text/turtle")))
        g.add((dist, DCAT.accessURL, URIRef(f"{REPO}/blob/main/{rel}")))
        g.add((dist, DCAT.downloadURL, URIRef(RAW + rel)))
        g.add((dist, DCAT.byteSize, Literal(path.stat().st_size, datatype=XSD.nonNegativeInteger)))
        g.add((dist, DCTERMS.license, DATASET_LICENSE))
        g.add((dist, VOID.triples, Literal(per_file[key]["triples"], datatype=INT)))

    # ---- provenance (PROV-O)
    kaggle_files = []
    for name in ("tmdb_5000_movies.csv", "tmdb_5000_credits.csv"):
        f = META["source_" + name.replace(".", "_")]
        kaggle_files.append(f)
        g.add((f, RDF.type, PROV.Entity))
        g.add((f, DCTERMS.title, Literal(name)))
        g.add((f, DCTERMS.format, Literal("text/csv")))
        g.add((f, PROV.wasDerivedFrom, KAGGLE))
        g.add((dataset, PROV.wasDerivedFrom, f))
    g.add((dataset, PROV.wasDerivedFrom, KAGGLE))
    g.add((dataset, PROV.wasAttributedTo, group))
    g.add((dataset, PROV.wasGeneratedBy, META["pipeline"]))

    pipeline = META["pipeline"]
    g.add((pipeline, RDF.type, PROV.Activity))
    g.add((pipeline, RDFS.label, Literal(
        "Movies LOD pipeline: CSV selection, CSV to RDF, Wikidata/DBpedia linking, awards", lang="en")))
    g.add((pipeline, PROV.wasAssociatedWith, group))
    for f in kaggle_files:
        g.add((pipeline, PROV.used, f))
    for src in (WIKIDATA, DBPEDIA):
        g.add((pipeline, PROV.used, src))
    for name in SCRIPTS:
        script = URIRef(f"{REPO}/blob/main/scripts/{name}")
        g.add((pipeline, PROV.used, script))
        g.add((script, RDF.type, PROV.Entity))
        g.add((script, DCTERMS.title, Literal(name)))
        g.add((script, DCTERMS.license, MIT))
    return g


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    graphs = {k: load(p) for k, p in DATA_FILES.items()}
    per_file = {k: stats(g) for k, g in graphs.items()}

    # consistency check against link_report.csv
    counted = {"wikidata": 0, "dbpedia": 0}
    for s in per_file.values():
        for key in counted:
            counted[key] += s["links"][key]
    reported = report_links()
    if counted != reported:
        sys.exit(f"link counts differ: TTL {counted} vs link_report.csv {reported}. "
                 "Regenerate the data files first.")

    movie_count = len(set(graphs["movies_linked"].subjects(RDF.type, SCHEMA_MOVIE)))
    previous_created = None
    if out.exists():
        previous_created = next(load(out).objects(META["dataset"], DCTERMS.created), None)
    g = build(per_file, len(load(ONTOLOGY_FILE)), movie_count, previous_created)
    out.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=out, format="turtle")
    print(f"Wrote {len(g)} triples to {out} "
          f"(dataset: {sum(s['triples'] for s in per_file.values())} triples, "
          f"links: {counted})")


if __name__ == "__main__":
    main()
