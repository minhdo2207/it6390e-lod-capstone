# Demo Script (Protege) — Minh

1. Open `ontology/movies.ttl` in Protege.
2. Import `data/processed/movies_linked.ttl` (File > Merge/Import, or just
   open it alongside - individuals get merged into the same model).
3. Reasoner > Start reasoner (HermiT). Open the Class Hierarchy tab and show
   `ActionMovie` / `ComedyMovie` / `AwardWinningDirector` now have inferred
   members, even though no movie was ever tagged with those classes by hand.
4. Window > Tabs > SPARQL Query. Run the queries from
   `sparql/sample_queries.rq` one by one, tie each result back to a
   competency question from `docs/PROJECT_PLAN.md`.
5. Rules tab (SWRL): paste in the rule from `ontology/rules.swrl`, re-run the
   reasoner, show a person who both directed and starred in the same movie
   getting classified as `ActorDirector`. Explain briefly why this needed a
   rule instead of a restriction (OWL property hierarchies only go
   specific -> general, can't combine two different properties like this).
6. Merge in `ontology/demo_inconsistency.ttl`, re-run the reasoner: it should
   report the ontology as inconsistent. Open the Explain button, walk
   through the justification (same pattern as the Russell's Paradox example
   from lecture). Remove the file again afterwards.
