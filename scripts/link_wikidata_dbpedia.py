"""Add owl:sameAs links from local movies and people to Wikidata and DBpedia.

Usage:
    python link_wikidata_dbpedia.py <input.ttl> <output.ttl> [report.csv]

Matching is done on identifiers, not names: our resource URIs end in the
TMDB id, and Wikidata records the TMDB id of films (P4947) and people
(P4985). A link is only added when exactly one Wikidata item carries that id.

The DBpedia link comes from DBpedia's own owl:sameAs statements pointing at
that Wikidata item, restricted to resources of the right type (dbo:Film or
dbo:Person) because that data is noisy - one film item can have a soundtrack
album or unrelated pages attached to it. Among the candidates we take the one
named after the item's English Wikipedia article (DBpedia resources are named
after those articles); if the article has been renamed since the DBpedia
snapshot, we take the candidate only when it is the single one left.

Redirect resources are never linked. DBpedia keeps the type and the sameAs
of an article that was later merged into another one, so a redirect can lead
to a different entity (an actor's page merged into a film, one director into
the page about a duo) and owl:sameAs would then be wrong. A redirect is
followed only when its target is the resource named after the item's English
Wikipedia article, which is the case of a simple rename.

The optional report CSV lists every resource with the links found, for
manual review.
"""

import csv
import sys
from collections import defaultdict
from urllib.parse import unquote

import requests
from rdflib import Graph, Namespace, OWL, RDF, URIRef

SCHEMA = Namespace("http://schema.org/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
DC = Namespace("http://purl.org/dc/elements/1.1/")

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
DBPEDIA_SPARQL = "https://dbpedia.org/sparql"
DBPEDIA_RESOURCE = "http://dbpedia.org/resource/"
ENWIKI_ARTICLE = "https://en.wikipedia.org/wiki/"
HEADERS = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "it6390e-group2-capstone/0.1 (HUST student project)",
}
BATCH_SIZE = 100


def run_query(endpoint, query):
    resp = requests.post(endpoint, data={"query": query}, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    return resp.json()["results"]["bindings"]


def batches(items):
    items = list(items)
    for i in range(0, len(items), BATCH_SIZE):
        yield items[i:i + BATCH_SIZE]


def unambiguous(candidates):
    """Keep only keys that map to exactly one value."""
    return {key: next(iter(values)) for key, values in candidates.items() if len(values) == 1}


def wikidata_by_tmdb_id(tmdb_ids, id_property):
    """Map TMDB id -> (Wikidata entity URI, English Wikipedia article title or None)."""
    candidates = defaultdict(set)
    for batch in batches(tmdb_ids):
        values = " ".join(f'"{tmdb_id}"' for tmdb_id in batch)
        query = f"""
        SELECT ?tmdb ?item ?article WHERE {{
            VALUES ?tmdb {{ {values} }}
            ?item wdt:{id_property} ?tmdb .
            OPTIONAL {{ ?article schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> . }}
        }}"""
        for b in run_query(WIKIDATA_SPARQL, query):
            article = b.get("article", {}).get("value")
            title = unquote(article[len(ENWIKI_ARTICLE):]) if article else None
            candidates[b["tmdb"]["value"]].add((b["item"]["value"], title))
    return unambiguous(candidates)


def dbpedia_by_wikidata(expected, dbpedia_class):
    """Take {Wikidata URI: DBpedia URI expected from the article name, or None}
    and return {Wikidata URI: DBpedia URI} for the links we can trust."""
    candidates = defaultdict(set)
    for batch in batches(expected):
        values = " ".join(f"<{uri}>" for uri in batch)
        query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        SELECT ?wd ?res ?target WHERE {{
            VALUES ?wd {{ {values} }}
            ?res owl:sameAs ?wd ; a dbo:{dbpedia_class} .
            FILTER(STRSTARTS(STR(?res), "{DBPEDIA_RESOURCE}"))
            OPTIONAL {{ ?res dbo:wikiPageRedirects ?target }}
        }}"""
        for b in run_query(DBPEDIA_SPARQL, query):
            wd_uri, res = b["wd"]["value"], b["res"]["value"]
            if "target" in b:
                # a redirect: follow it only when it is a plain rename, i.e.
                # it leads to the resource named after the item's article
                res = b["target"]["value"]
                if unquote(res) != expected[wd_uri]:
                    continue
            candidates[wd_uri].add(res)

    links = {}
    for wd_uri, resources in candidates.items():
        by_name = [res for res in resources if unquote(res) == expected[wd_uri]]
        if by_name:
            links[wd_uri] = by_name[0]
        elif len(resources) == 1:
            links[wd_uri] = next(iter(resources))
    return links


def tmdb_id(uri):
    return str(uri).rsplit("/", 1)[-1]


def main():
    if len(sys.argv) not in (3, 4):
        print(__doc__)
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]
    report_path = sys.argv[3] if len(sys.argv) == 4 else None

    g = Graph()
    g.parse(input_path, format="turtle")
    g.bind("owl", OWL)
    # rdflib pre-binds "schema" to https://schema.org/, replace it
    g.bind("schema", SCHEMA, replace=True)

    # (kind, Wikidata property holding the TMDB id, DBpedia class, resources, label property)
    groups = [
        ("movie", "P4947", "Film", sorted(set(g.subjects(RDF.type, SCHEMA.Movie))), DC.title),
        ("person", "P4985", "Person", sorted(set(g.subjects(RDF.type, FOAF.Person))), FOAF.name),
    ]

    report = []
    for kind, id_property, dbpedia_class, resources, label_property in groups:
        wikidata = wikidata_by_tmdb_id([tmdb_id(r) for r in resources], id_property)
        dbpedia = dbpedia_by_wikidata({
            wd_uri: DBPEDIA_RESOURCE + title if title else None
            for wd_uri, title in wikidata.values()
        }, dbpedia_class)

        for resource in resources:
            wd_uri, _ = wikidata.get(tmdb_id(resource), (None, None))
            db_uri = dbpedia.get(wd_uri)
            if wd_uri:
                g.add((resource, OWL.sameAs, URIRef(wd_uri)))
            if db_uri:
                g.add((resource, OWL.sameAs, URIRef(db_uri)))
            report.append({
                "kind": kind,
                "uri": str(resource),
                "label": str(g.value(resource, label_property) or ""),
                "wikidata": wd_uri or "",
                "dbpedia": db_uri or "",
            })

        total = len(resources)
        print(f"{kind}: {total} resources, {len(wikidata)} linked to Wikidata, "
              f"{len(dbpedia)} linked to DBpedia")

    g.serialize(destination=output_path, format="turtle")
    print(f"Wrote {len(g)} triples to {output_path}")

    if report_path:
        with open(report_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(report[0]))
            writer.writeheader()
            writer.writerows(report)
        print(f"Wrote link report to {report_path}")


if __name__ == "__main__":
    main()
