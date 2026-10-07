"""Write the two single-file ontologies used for the Protege demo.

Usage:
    python make_protege_demo.py [output_dir]      # default: ~/Desktop

Protege reasons over one ontology at a time, and our ontology, linked data
and awards live in three Turtle files without an ontology header. Opening
them one by one and merging is fiddly during a live demo, so this script
merges them into:

    demo_all.ttl      ontology + movies_linked.ttl + awards.ttl
    demo_all_bad.ttl  the same plus ontology/demo_inconsistency.ttl

Both files get an owl:Ontology header and the ont:/schema: prefixes, so
Protege shows names like ont:ActionMovie under View > Render by prefixed
name. They are generated files: do not commit them.
"""

import sys
from pathlib import Path

from rdflib import Graph, Namespace, OWL, RDF, URIRef

ROOT = Path(__file__).resolve().parent.parent
ONT = Namespace("http://it6390e-group2.example.org/ontology/")
SCHEMA = Namespace("http://schema.org/")

FILES = [
    "ontology/movies.ttl",
    "data/processed/movies_linked.ttl",
    "data/processed/awards.ttl",
]
BAD_MOVIE = "ontology/demo_inconsistency.ttl"


def write(graph, ontology_name, path):
    # exactly one ontology header per file
    graph.remove((None, RDF.type, OWL.Ontology))
    graph.add((URIRef(ONT[ontology_name]), RDF.type, OWL.Ontology))
    graph.bind("ont", ONT)
    # rdflib pre-binds "schema" to https://schema.org/, replace it
    graph.bind("schema", SCHEMA, replace=True)
    graph.serialize(destination=path, format="turtle")
    print(f"Wrote {len(graph)} triples to {path}")


def main():
    out_dir = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home() / "Desktop"
    out_dir.mkdir(parents=True, exist_ok=True)

    g = Graph()
    for f in FILES:
        g.parse(ROOT / f, format="turtle")
    write(g, "demo-all", out_dir / "demo_all.ttl")

    g.parse(ROOT / BAD_MOVIE, format="turtle")
    write(g, "demo-all-bad", out_dir / "demo_all_bad.ttl")


if __name__ == "__main__":
    main()
