"""Convert the raw movies CSV into a 4-star Turtle file.

Usage:
    python csv_to_rdf.py <input.csv> <output.ttl>

Expected CSV columns:
    id, title, year, director_id, director_name, genre, studio, country
Optional columns ("|"-separated, same order in both):
    cast_ids, cast_names
"""

import csv
import re
import sys

from rdflib import Graph, Literal, Namespace, RDF, RDFS, XSD

BASE = Namespace("http://it6390e-group2.example.org/resource/")
ONT = Namespace("http://it6390e-group2.example.org/ontology/")
SCHEMA = Namespace("http://schema.org/")
DBO = Namespace("http://dbpedia.org/ontology/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
DC = Namespace("http://purl.org/dc/elements/1.1/")


def slug(name, sep="-"):
    """Lowercase ASCII-safe URI segment, e.g. "Warner Bros." -> "warner-bros"."""
    return re.sub(r"[^a-z0-9]+", sep, name.lower()).strip(sep)


def build_graph(rows):
    g = Graph()
    g.bind("ex", BASE)
    g.bind("ont", ONT)
    # rdflib pre-binds "schema" to https://schema.org/, replace it
    g.bind("schema", SCHEMA, replace=True)
    g.bind("dbo", DBO)
    g.bind("foaf", FOAF)
    g.bind("dc", DC)

    for row in rows:
        movie_uri = BASE[f"movie/{row['id']}"]
        g.add((movie_uri, RDF.type, SCHEMA.Movie))
        g.add((movie_uri, DC.title, Literal(row["title"])))
        g.add((movie_uri, ONT.releaseYear, Literal(int(row["year"]), datatype=XSD.integer)))

        if row.get("director_id"):
            director_uri = BASE[f"person/{row['director_id']}"]
            g.add((director_uri, RDF.type, FOAF.Person))
            g.add((director_uri, RDF.type, ONT.Director))
            g.add((director_uri, FOAF.name, Literal(row["director_name"])))
            g.add((movie_uri, DBO.director, director_uri))

        if row.get("cast_ids"):
            cast = zip(row["cast_ids"].split("|"), row["cast_names"].split("|"))
            for actor_id, actor_name in cast:
                actor_uri = BASE[f"person/{actor_id}"]
                g.add((actor_uri, RDF.type, FOAF.Person))
                g.add((actor_uri, RDF.type, ONT.Actor))
                g.add((actor_uri, FOAF.name, Literal(actor_name)))
                g.add((movie_uri, DBO.starring, actor_uri))

        if row.get("genre"):
            # must match the genre individuals in ontology/movies.ttl
            # (:genre_action, :genre_comedy) or the hasValue restrictions
            # behind ActionMovie/ComedyMovie never fire
            genre_uri = ONT[f"genre_{slug(row['genre'], '_')}"]
            g.add((genre_uri, RDF.type, ONT.Genre))
            g.add((genre_uri, RDFS.label, Literal(row["genre"], lang="en")))
            g.add((movie_uri, ONT.hasGenre, genre_uri))

        if row.get("studio"):
            studio_uri = ONT[f"studio/{slug(row['studio'])}"]
            g.add((studio_uri, RDF.type, ONT.Studio))
            g.add((studio_uri, RDFS.label, Literal(row["studio"], lang="en")))
            g.add((movie_uri, ONT.producedBy, studio_uri))

        if row.get("country"):
            country_uri = ONT[f"country/{slug(row['country'])}"]
            g.add((country_uri, RDF.type, ONT.Country))
            g.add((country_uri, RDFS.label, Literal(row["country"], lang="en")))
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
