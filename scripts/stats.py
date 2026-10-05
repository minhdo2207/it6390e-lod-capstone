"""Print the dataset numbers used in the report results section.

Usage:
    python stats.py

Loads the same files as sparql_cli.py (ontology, linked movie data, awards)
and prints: total triples, individuals per class, owl:sameAs links per
target, movies per genre and the top 5 directors by number of movies.

Class counts use the types asserted in the data, no reasoner is run, so
defined classes such as ActionMovie are not listed.
"""

from pathlib import Path

from rdflib import Graph

ROOT = Path(__file__).resolve().parent.parent
FILES = [
    "ontology/movies.ttl",
    "data/processed/movies_linked.ttl",
    "data/processed/awards.ttl",
]

PREFIXES = """
PREFIX ont:    <http://it6390e-group2.example.org/ontology/>
PREFIX dbo:    <http://dbpedia.org/ontology/>
PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
PREFIX schema: <http://schema.org/>
PREFIX owl:    <http://www.w3.org/2002/07/owl#>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
"""

# Movies and people are typed with the reused vocabulary terms in the data;
# the ontology declares those equivalent to ont:Movie / ont:Person.
CLASSES = [
    ("Movie", "schema:Movie"),
    ("Person", "foaf:Person"),
    ("Director", "ont:Director"),
    ("Actor", "ont:Actor"),
    ("Genre", "ont:Genre"),
    ("Studio", "ont:Studio"),
    ("Country", "ont:Country"),
]
LINK_TARGETS = [
    ("wikidata.org", "http://www.wikidata.org/entity/"),
    ("dbpedia.org", "http://dbpedia.org/resource/"),
]


def load_graph():
    g = Graph()
    for f in FILES:
        g.parse(ROOT / f, format="turtle")
    return g


def count(g, pattern):
    query = PREFIXES + f"SELECT (COUNT(DISTINCT ?s) AS ?n) WHERE {{ {pattern} }}"
    return int(next(iter(g.query(query)))[0])


def print_table(title, header, rows):
    rows = [[str(v) for v in row] for row in rows]
    widths = [max(len(h), *(len(r[i]) for r in rows)) for i, h in enumerate(header)]
    print(title)
    print("  ".join(h.ljust(w) for h, w in zip(header, widths)).rstrip())
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print("  ".join(v.ljust(w) for v, w in zip(row, widths)).rstrip())
    print()


def main():
    g = load_graph()

    print(f"Total triples: {len(g)}\n")

    print_table(
        "Individuals per class",
        ["class", "individuals"],
        [(name, count(g, f"?s a {term}")) for name, term in CLASSES],
    )

    print_table(
        "owl:sameAs links per target",
        ["target", "movies", "people", "total"],
        [
            (
                target,
                movies := count(g, f'?s a schema:Movie ; owl:sameAs ?o . FILTER(STRSTARTS(STR(?o), "{prefix}"))'),
                people := count(g, f'?s a foaf:Person ; owl:sameAs ?o . FILTER(STRSTARTS(STR(?o), "{prefix}"))'),
                movies + people,
            )
            for target, prefix in LINK_TARGETS
        ],
    )

    print_table(
        "Movies per genre",
        ["genre", "movies"],
        g.query(PREFIXES + """
            SELECT ?genre (COUNT(DISTINCT ?movie) AS ?n) WHERE {
                ?movie ont:hasGenre ?g .
                ?g rdfs:label ?genre .
            }
            GROUP BY ?genre
            ORDER BY DESC(?n) ?genre
        """),
    )

    print_table(
        "Top 5 directors by number of movies",
        ["director", "movies"],
        g.query(PREFIXES + """
            SELECT ?name (COUNT(DISTINCT ?movie) AS ?n) WHERE {
                ?movie dbo:director ?d .
                ?d foaf:name ?name .
            }
            GROUP BY ?d ?name
            ORDER BY DESC(?n) ?name
            LIMIT 5
        """),
    )


if __name__ == "__main__":
    main()
