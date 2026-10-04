"""Terminal SPARQL interface over the ontology + movie data.

Usage:
    python sparql_cli.py                    # interactive prompt
    python sparql_cli.py -n 3               # run query #3 from sparql/sample_queries.rq
    python sparql_cli.py -q "SELECT ..."    # run a one-off query
    python sparql_cli.py -f my_query.rq     # run a query from a file

In the prompt, end a query with a blank line to run it, ":list" shows the
sample queries, ":n" (e.g. ":3") runs one of them, ":quit" exits.
"""

import argparse
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

from rdflib import Graph
from rdflib.plugins.sparql import evaluate as sparql_evaluate

ROOT = Path(__file__).resolve().parent.parent
FILES = [
    "ontology/movies.ttl",
    "data/processed/movies_linked.ttl",
    "data/processed/awards.ttl",
]
SAMPLE_FILES = [
    ROOT / "sparql" / "sample_queries.rq",
    ROOT / "sparql" / "federated_queries.rq",  # SERVICE queries, need internet
]
USER_AGENT = "it6390e-group2-capstone/0.1 (HUST student project)"


# Public endpoints (DBpedia, Wikidata) are rate limited and answer 429/503 when
# they are busy; their operators ask clients to wait and retry.
RETRY_CODES = {429, 502, 503, 504}
MAX_ATTEMPTS = 4
MIN_INTERVAL = 1.0  # seconds between two SERVICE requests
_last_call = 0.0


def _retry_delay(error, attempt):
    """Seconds to wait before retrying: Retry-After if given, else 2, 4, 8."""
    try:
        return min(int(error.headers.get("Retry-After")), 30)
    except (TypeError, ValueError, AttributeError):
        return 2 ** attempt


def _urlopen_for_service(request, *args, **kwargs):
    """rdflib calls urlopen() for every SERVICE request. Add a descriptive
    User-Agent (Wikidata asks for one), a timeout so a dead endpoint does not
    hang, a pause between requests, and retries when the endpoint is busy."""
    global _last_call
    request.add_header("User-Agent", USER_AGENT)
    kwargs.setdefault("timeout", 90)
    for attempt in range(1, MAX_ATTEMPTS + 1):
        pause = MIN_INTERVAL - (time.monotonic() - _last_call)
        if pause > 0:
            time.sleep(pause)
        try:
            return urlopen(request, *args, **kwargs)
        except HTTPError as e:
            if e.code not in RETRY_CODES or attempt == MAX_ATTEMPTS:
                raise
            delay = _retry_delay(e, attempt)
            print(f"  {request.full_url.split('?')[0]}: HTTP {e.code}, retrying in {delay}s "
                  f"({attempt}/{MAX_ATTEMPTS - 1})", file=sys.stderr)
            time.sleep(delay)
        finally:
            _last_call = time.monotonic()


def describe_error(e):
    """One-line message that names the endpoint that failed."""
    url = getattr(e, "url", None)
    where = f" at {url.split('?')[0]}" if url else ""
    return f"{e}{where}"


sparql_evaluate.urlopen = _urlopen_for_service


def load_graph():
    g = Graph()
    for f in FILES:
        g.parse(ROOT / f, format="turtle")
    return g


def sample_queries():
    """Split the .rq files into {number: (title, query)}, prefixes included."""
    queries = {}
    for path in SAMPLE_FILES:
        text = path.read_text(encoding="utf-8")
        prefixes = "\n".join(l for l in text.splitlines() if l.startswith("PREFIX"))
        for block in re.split(r"\n(?=# \d+\.)", text)[1:]:
            title, _, body = block.partition("\n")
            number = int(re.match(r"# (\d+)\.", title).group(1))
            if number in queries:
                sys.exit(f"duplicate query number {number} in {path.name}")
            queries[number] = (title.lstrip("# "), prefixes + "\n" + body)
    return queries


def run(g, query):
    result = g.query(query)
    if result.type == "ASK":
        print(bool(result.askAnswer))
        return
    if result.type != "SELECT":
        print(result.serialize(format="turtle").decode())
        return
    rows = [[("" if v is None else str(v)) for v in row] for row in result]
    header = [str(v) for v in result.vars]
    widths = [max(len(h), *(len(r[i]) for r in rows)) if rows else len(h) for i, h in enumerate(header)]
    print("  ".join(h.ljust(w) for h, w in zip(header, widths)))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print("  ".join(c.ljust(w) for c, w in zip(r, widths)))
    print(f"({len(rows)} rows)")


def repl(g, samples):
    print("SPARQL prompt. Blank line runs the query, :list for samples, :quit to exit.")
    buf = []
    while True:
        try:
            line = input("sparql> " if not buf else "     .. ")
        except EOFError:
            break
        cmd = line.strip()
        if cmd in (":quit", ":q"):
            break
        if cmd == ":list" and not buf:
            for n, (title, _) in sorted(samples.items()):
                print(f"  :{n}  {title}")
            continue
        if re.fullmatch(r":\d+", cmd) and not buf:
            n = int(cmd[1:])
            if n in samples:
                try:
                    run(g, samples[n][1])
                except Exception as e:
                    print("error:", describe_error(e))
            else:
                print("no such sample query")
            continue
        if cmd == "" and buf:
            try:
                run(g, "\n".join(buf))
            except Exception as e:
                print("error:", describe_error(e))
            buf = []
        elif cmd:
            buf.append(line)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", type=int, help="run sample query number N")
    ap.add_argument("-q", help="run this query string")
    ap.add_argument("-f", help="run the query in this file")
    args = ap.parse_args()

    g = load_graph()
    samples = sample_queries()

    try:
        if args.n:
            if args.n not in samples:
                sys.exit(f"no sample query #{args.n}")
            run(g, samples[args.n][1])
        elif args.q:
            run(g, args.q)
        elif args.f:
            run(g, Path(args.f).read_text(encoding="utf-8"))
        else:
            repl(g, samples)
    except OSError as e:  # URLError/HTTPError/timeout from a SERVICE call
        sys.exit(f"error: could not reach the remote endpoint: {describe_error(e)}. "
                 "Federated queries need internet access; the endpoint may be busy, "
                 "try again in a minute.")


if __name__ == "__main__":
    main()
