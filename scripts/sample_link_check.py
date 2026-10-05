"""Draw the reproducible sample used for the manual link quality check.

Usage:
    python sample_link_check.py [link_report.csv]

Picks 15 movies and 15 people at random (fixed seed) from the rows of
link_report.csv that have at least one link, and prints them as CSV with
the facts needed to judge each link by hand: release year and director for
movies, one movie they worked on for people.
"""

import csv
import random
import sys
from pathlib import Path

from rdflib import Graph, Namespace, URIRef

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "data" / "processed" / "link_report.csv"
DATA = ROOT / "data" / "processed" / "movies_linked.ttl"

SEED = 42
PER_KIND = 15

ONT = Namespace("http://it6390e-group2.example.org/ontology/")
DBO = Namespace("http://dbpedia.org/ontology/")
DC = Namespace("http://purl.org/dc/elements/1.1/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")


def local_facts(g, kind, uri):
    """Short description of the local resource to compare the links against."""
    if kind == "movie":
        director = g.value(uri, DBO.director)
        return f"{g.value(uri, ONT.releaseYear)}, directed by {g.value(director, FOAF.name)}"
    for role, prop in (("director", DBO.director), ("actor", DBO.starring)):
        movie = next(iter(sorted(g.subjects(prop, uri))), None)
        if movie:
            return f"{role} of {g.value(movie, DC.title)} ({g.value(movie, ONT.releaseYear)})"
    return ""


def main():
    report_path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPORT
    with open(report_path, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["wikidata"] or r["dbpedia"]]

    random.seed(SEED)
    sample = []
    for kind in ("movie", "person"):
        sample += random.sample([r for r in rows if r["kind"] == kind], PER_KIND)

    g = Graph()
    g.parse(DATA, format="turtle")

    writer = csv.writer(sys.stdout)
    writer.writerow(["kind", "uri", "label", "local_facts", "wikidata", "dbpedia"])
    for r in sample:
        facts = local_facts(g, r["kind"], URIRef(r["uri"]))
        writer.writerow([r["kind"], r["uri"], r["label"], facts, r["wikidata"], r["dbpedia"]])


if __name__ == "__main__":
    main()
