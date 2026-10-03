"""Add Oscar Best Director awards from Wikidata for the people we already
linked, so AwardWinningDirector has members to infer.

Usage:
    python add_awards.py <link_report.csv> <output.ttl>

Reads the people rows of link_report.csv (kind, uri, label, wikidata, dbpedia),
asks Wikidata which of them hold "Academy Award for Best Director" (Q103360)
via P166, and writes ont:hasAward triples.
"""

import csv
import sys

import requests
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef

ONT = Namespace("http://it6390e-group2.example.org/ontology/")
WD_SPARQL = "https://query.wikidata.org/sparql"
BEST_DIRECTOR = "Q103360"
AWARD = ONT["award_oscar_best_director"]


def winners(qids):
    values = " ".join(f"wd:{q}" for q in qids)
    query = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    SELECT DISTINCT ?p WHERE {{
      VALUES ?p {{ {values} }}
      ?p wdt:P166 wd:{BEST_DIRECTOR} .
    }}
    """
    resp = requests.get(
        WD_SPARQL,
        params={"query": query, "format": "json"},
        headers={"User-Agent": "it6390e-lod-capstone/0.1 (student project)"},
        timeout=60,
    )
    resp.raise_for_status()
    return {b["p"]["value"].rsplit("/", 1)[1] for b in resp.json()["results"]["bindings"]}


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    people = {}
    with open(sys.argv[1], encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["kind"] == "person" and row["wikidata"]:
                people[row["wikidata"].rsplit("/", 1)[1]] = row["uri"]

    qids = sorted(people)
    won = set()
    for i in range(0, len(qids), 100):
        won |= winners(qids[i : i + 100])

    g = Graph()
    g.bind("ont", ONT)
    g.add((AWARD, RDF.type, ONT.Award))
    g.add((AWARD, RDFS.label, Literal("Academy Award for Best Director", lang="en")))
    for qid in sorted(won):
        g.add((URIRef(people[qid]), ONT.hasAward, AWARD))

    g.serialize(destination=sys.argv[2], format="turtle")
    print(f"{len(won)} of {len(people)} linked people hold the award -> {sys.argv[2]}")


if __name__ == "__main__":
    main()
