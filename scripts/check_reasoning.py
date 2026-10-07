"""Run HermiT over ontology + data and print what gets inferred.

Same thing we do by hand in Protege (Reasoner > Start), but scriptable so we
can re-check after every change to the ontology or the data.

Usage:
    python check_reasoning.py            # classification on the clean data
    python check_reasoning.py --demo     # also load demo_inconsistency.ttl

Needs: pip install owlready2 rdflib, and Java on PATH (HermiT is bundled).
"""

import sys
import tempfile
from pathlib import Path

from owlready2 import (
    OwlReadyInconsistentOntologyError,
    World,
    sync_reasoner_hermit,
)
from rdflib import Graph, URIRef

ROOT = Path(__file__).resolve().parent.parent
ONT = "http://it6390e-group2.example.org/ontology/"
LOCAL = "http://it6390e-group2.example.org/resource/"
DBO = "http://dbpedia.org/ontology/"


def load_world(files):
    """owlready2 can't read Turtle, so merge with rdflib and hand it RDF/XML."""
    g = Graph()
    for f in files:
        g.parse(ROOT / f, format="turtle")
    tmp = tempfile.NamedTemporaryFile(suffix=".owl", delete=False)
    g.serialize(destination=tmp.name, format="xml")
    world = World()
    world.get_ontology("file://" + tmp.name).load()
    return world


def check_cast_roles(files):
    """dbo:starring must agree with the n-ary cast roles: the ontology says
    hasCastRole o playedBy implies starring, and the data keeps both."""
    g = Graph()
    for f in files:
        g.parse(ROOT / f, format="turtle")
    starring = set(g.subject_objects(URIRef(DBO + "starring")))
    via_roles = {
        (movie, actor)
        for movie, role in g.subject_objects(URIRef(ONT + "hasCastRole"))
        for actor in g.objects(role, URIRef(ONT + "playedBy"))
    }
    print(f"cast roles: {len(via_roles)} (movie, actor) pairs through roles, "
          f"{len(starring)} through dbo:starring")
    if starring != via_roles:
        print(f"MISMATCH: {len(starring - via_roles)} starring without a role, "
              f"{len(via_roles - starring)} roles without starring")
        return False
    return True


def members(world, name):
    # owl:sameAs makes the Wikidata/DBpedia URIs count as the same individual,
    # so only count our own resources or every movie shows up three times.
    cls = world[ONT + name]
    if not cls:
        return []
    return sorted(i.iri for i in cls.instances() if i.iri.startswith(LOCAL))


def add_actor_director_rule(world):
    """Same rule as ontology/rules.swrl."""
    from owlready2 import Imp

    onto = world.get_ontology("http://it6390e-group2.example.org/rules")
    with onto:
        rule = Imp()
        rule.set_as_rule(
            "director(?m, ?p), starring(?m, ?p) -> ActorDirector(?p)",
            namespaces=[world.get_namespace(DBO), world.get_namespace(ONT)],
        )


def run(files, label):
    print(f"== {label}")
    world = load_world(files)
    add_actor_director_rule(world)
    try:
        with world.get_ontology("http://it6390e-group2.example.org/inferred"):
            sync_reasoner_hermit(world, infer_property_values=False)
    except OwlReadyInconsistentOntologyError:
        print("ontology is INCONSISTENT")
        return False
    for name in ("ActionMovie", "ComedyMovie", "AwardWinningDirector", "ActorDirector", "CastRole"):
        found = members(world, name)
        print(f"{name}: {len(found)}")
    return True


def main():
    base = [
        "ontology/movies.ttl",
        "data/processed/movies_linked.ttl",
        "data/processed/awards.ttl",
    ]
    ok = run(base, "clean data")
    if not ok:
        sys.exit(1)
    if not check_cast_roles(base):
        sys.exit(1)

    if "--demo" in sys.argv:
        bad = run(base + ["ontology/demo_inconsistency.ttl"], "with demo_inconsistency.ttl")
        if bad:
            print("expected an inconsistency but the reasoner found none")
            sys.exit(1)


if __name__ == "__main__":
    main()
