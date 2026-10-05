# Demo Script (Protege) — Minh

1. Open `ontology/movies.ttl` in Protege.
2. Merge in `data/processed/movies_linked.ttl` and `data/processed/awards.ttl`
   (File > Open, "Merge into current ontology"). Individuals end up in the same
   model.
3. Reasoner > Start reasoner (HermiT). Open the Class Hierarchy tab and show
   `ActionMovie` (29), `ComedyMovie` (16) and `AwardWinningDirector` (32) now
   have inferred members, even though nobody was tagged with those classes by
   hand. Same counts as `python scripts/check_reasoning.py`.
4. Window > Tabs > SPARQL Query. Run the queries from
   `sparql/sample_queries.rq` one by one, tie each result back to a
   competency question from `docs/PROJECT_PLAN.md`.
   For the federated part (`SERVICE` to Wikidata/DBpedia) use the terminal,
   `python scripts/sparql_cli.py -n 6` (and 7-15), from
   `sparql/federated_queries.rq`. Needs internet; run them once before the
   demo to check the endpoints are up.
5. Rules tab (SWRL): paste in the rule from `ontology/rules.swrl`, re-run the
   reasoner, show a person who both directed and starred in the same movie
   getting classified as `ActorDirector` (5 people, e.g. Clint Eastwood, Mel
   Gibson, Kevin Costner). Explain briefly why this needed a
   rule instead of a restriction (OWL property hierarchies only go
   specific -> general, can't combine two different properties like this).
6. Merge in `ontology/demo_inconsistency.ttl`, re-run the reasoner: it should
   report the ontology as inconsistent. Open the Explain button, walk
   through the justification (same pattern as the Russell's Paradox example
   from lecture). Remove the file again afterwards.
