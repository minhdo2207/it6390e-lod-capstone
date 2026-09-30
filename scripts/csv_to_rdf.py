"""Convert the raw movies CSV into a 4-star Turtle file.

Usage:
    python csv_to_rdf.py <input.csv> <output.ttl>

Expected CSV columns:
    id, title, year, director_id, director_name, genre, studio, country
"""

import csv
import sys

from rdflib import Graph, Literal, Namespace, RDF, XSD

BASE = Namespace("http://it6390e-group2.example.org/resource/")
ONT = Namespace("http://it6390e-group2.example.org/ontology/")
SCHEMA = Namespace("http://schema.org/")
DBO = Namespace("http://dbpedia.org/ontology/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
DC = Namespace("http://purl.org/dc/elements/1.1/")


def build_graph(rows):
    g = Graph()
    g.bind("ex", BASE)
    g.bind("ont", ONT)
    g.bind("schema", SCHEMA)
    g.bind("dbo", DBO)
    g.bind("foaf", FOAF)
    g.bind("dc", DC)

    for row in rows:
        movie_uri = BASE[f"movie/{row['id']}"]
        g.add((movie_uri, RDF.type, SCHEMA.Movie))
        g.add((movie_uri, DC.title, Literal(row["title"])))
        g.add((movie_uri, ONT.releaseYear, Literal(row["year"], datatype=XSD.gYear)))

        if row.get("director_id"):
            director_uri = BASE[f"person/{row['director_id']}"]
            g.add((director_uri, RDF.type, FOAF.Person))
            g.add((director_uri, RDF.type, ONT.Director))
            g.add((director_uri, FOAF.name, Literal(row["director_name"])))
            g.add((movie_uri, DBO.director, director_uri))

        if row.get("genre"):
            genre_uri = ONT[f"genre/{row['genre'].lower().replace(' ', '-')}"]
            g.add((genre_uri, RDF.type, ONT.Genre))
            g.add((movie_uri, ONT.hasGenre, genre_uri))

        if row.get("studio"):
            studio_uri = ONT[f"studio/{row['studio'].lower().replace(' ', '-')}"]
            g.add((studio_uri, RDF.type, ONT.Studio))
            g.add((movie_uri, ONT.producedBy, studio_uri))

        if row.get("country"):
            country_uri = ONT[f"country/{row['country'].lower().replace(' ', '-')}"]
            g.add((country_uri, RDF.type, ONT.Country))
            g.add((movie_uri, ONT.producedIn, country_uri))

    return g


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    with open(input_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    graph = build_graph(rows)
    graph.serialize(destination=output_path, format="turtle")
    print(f"Wrote {len(graph)} triples to {output_path}")


if __name__ == "__main__":
    main()
