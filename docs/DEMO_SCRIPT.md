# Demo Script (Protégé) — Minh

Checked on Protégé 5.6.9 (macOS, Apple Silicon) on 7 October 2026. The step
marked *(not yet run in Protégé)* was only checked from the terminal.

## Before the talk

1. Generate the two demo files (they are not committed):
   ```bash
   python scripts/make_protege_demo.py            # writes ~/Desktop/demo_all.ttl and demo_all_bad.ttl
   ```
   `demo_all.ttl` = ontology + linked data + awards in one file;
   `demo_all_bad.ttl` = the same plus the bad movie from `ontology/demo_inconsistency.ttl`.
2. Open Protégé, **File > Open** `demo_all.ttl`.
3. **View > Render by prefixed name**, so classes show as `ont:ActionMovie`
   and the DL Query box accepts that name.
4. **Reasoner > HermiT**, then **Reasoner > Start reasoner**. It takes about
   **3 minutes** (most of it on "Computing instances for all object
   properties"), so do this before the talk, not live.
5. Add the SWRL rule now too (step 4 below) and let the reasoner synchronize
   again: about **4 minutes**.
6. Run the federated queries once (`python scripts/sparql_cli.py -n 6`, `-n 7`)
   to check that Wikidata and DBpedia are answering.

## Live

1. **Ontology.** Tab **Entities > Classes**: show `ont:Movie`, `ont:Person`
   with `Director` and `Actor`, then `ont:ActionMovie` and its *Equivalent To*
   `hasGenre value genre_action`.

2. **Reasoning.** **Window > Tabs > DL Query**. Tick **Instances** only, type
   the class, press **Esc** to close the autocomplete popup, click
   **Execute** (not *Add to ontology*, which opens a "Create a new Class"
   dialog).

   | Query | Protégé shows | Our resources |
   |---|---|---|
   | `ont:ActionMovie` | 87 | 29 movies |
   | `ont:ComedyMovie` | 48 | 16 movies |
   | `ont:AwardWinningDirector` | 95 | 32 directors (one has no DBpedia link) |
   | `ont:CastRole` | 750 | 750 roles |
   | `ont:ActorDirector` (after the rule) | 15 | 5 people |

   The lists are about three times longer because `owl:sameAs` makes each
   movie or person the same individual as its Wikidata and DBpedia IRIs, so
   all three names are listed. Say so: it is the 5th star at work. Same counts
   as `python scripts/check_reasoning.py`.

3. **SPARQL** *(not yet run in Protégé)*. **Window > Tabs > SPARQL Query**, paste the `PREFIX` lines from
   the top of `sparql/sample_queries.rq` plus one query (1, 3 or 5). This tab
   only sees asserted triples, so do not query the defined classes here.
   The terminal gives the same results:
   `python scripts/sparql_cli.py -n 3`. Federated and cast-role queries run
   from the terminal: `-n 6`, `-n 7`, `-n 16`.

4. **SWRL rule.** **Window > Tabs > SWRLTab > New**, rule:
   ```
   ont:Movie(?m) ^ dbo:director(?m, ?p) ^ dbo:starring(?m, ?p) -> ont:ActorDirector(?p)
   ```
   The editor shows Status "Ok"; click **Ok**, then **Reasoner > Synchronize
   reasoner**. DL Query `ont:ActorDirector`: Clint Eastwood, Kevin Costner,
   Mel Gibson, Terry Gilliam, Woody Allen. Explain why this needs a rule: OWL
   cannot require the same person on two different properties of one movie.

5. **Inconsistency.** **File > Open** `demo_all_bad.ttl` (it opens in a new
   window), **Reasoner > Start reasoner**: within seconds Protégé shows "Help
   for inconsistent ontologies". Click **Explain**: the justification lists
   five axioms, ActionMovie DisjointWith ComedyMovie, the two `hasValue`
   definitions, and the two `hasGenre` assertions of `ex:movie_demo_bad`.
   Walk through it (same pattern as Russell's paradox in the lecture).
   `python scripts/check_reasoning.py --demo` shows the same result.

When closing Protégé, choose **Don't save**: the rule and settings only live
in the session, the generated files stay as they are.
