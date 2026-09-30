"""Add owl:sameAs links from local movie resources to DBpedia, by matching
on title + release year to avoid mismatching remakes/sequels.

Usage:
    python link_dbpedia.py <input.ttl> <output.ttl>

This only adds a link when a single, confident match is found. Ambiguous or
missing matches are left unlinked rather than guessed - see the LOD lecture
notes on owl:sameAs misuse for why guessing is a bad idea here.
"""

import sys

import requests
from rdflib import Graph, Literal, Namespace, OWL, RDF, URIRef

ONT = Namespace("http://it6390e-group2.example.org/ontology/")
DC = Namespace("http://purl.org/dc/elements/1.1/")

DBPEDIA_SPARQL = "https://dbpedia.org/sparql"


def find_dbpedia_match(title, year):
    query = f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?film WHERE {{
        ?film a dbo:Film ;
              rdfs:label ?label ;
              dbo:releaseDate ?date .
        FILTER(lang(?label) = "en" && CONTAINS(?label, "{title}"))
        FILTER(YEAR(?date) = {year})
    }}
    LIMIT 5
    """
    resp = requests.get(
        DBPEDIA_SPARQL,
        params={"query": query, "format": "application/sparql-results+json"},
        timeout=15,
    )
    resp.raise_for_status()
    bindings = resp.json()["results"]["bindings"]

    if len(bindings) == 1:
        return bindings[0]["film"]["value"]
    return None  # zero or ambiguous matches: do not guess


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    g = Graph()
    g.parse(input_path, format="turtle")

    linked, skipped = 0, 0
    for movie_uri, title_lit in g.subject_objects(DC.title):
        year_lit = g.value(movie_uri, ONT.releaseYear)
        if year_lit is None:
            skipped += 1
            continue

        match = find_dbpedia_match(str(title_lit), str(year_lit))
        if match:
            g.add((movie_uri, OWL.sameAs, URIRef(match)))
            linked += 1
        else:
            skipped += 1

    g.serialize(destination=output_path, format="turtle")
    print(f"Linked {linked} movies, skipped {skipped} (no confident match).")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
