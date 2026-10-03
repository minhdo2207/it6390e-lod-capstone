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
from pathlib import Path

from rdflib import Graph

ROOT = Path(__file__).resolve().parent.parent
FILES = [
    "ontology/movies.ttl",
    "data/processed/movies_linked.ttl",
    "data/processed/awards.ttl",
]
SAMPLES = ROOT / "sparql" / "sample_queries.rq"


def load_graph():
    g = Graph()
    for f in FILES:
        g.parse(ROOT / f, format="turtle")
    return g


def sample_queries():
    """Split sample_queries.rq into {number: (title, query)}, prefixes included."""
    text = SAMPLES.read_text(encoding="utf-8")
    prefixes = "\n".join(l for l in text.splitlines() if l.startswith("PREFIX"))
    queries = {}
    for block in re.split(r"\n(?=# \d+\.)", text)[1:]:
        title, _, body = block.partition("\n")
        number = int(re.match(r"# (\d+)\.", title).group(1))
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
                run(g, samples[n][1])
            else:
                print("no such sample query")
            continue
        if cmd == "" and buf:
            try:
                run(g, "\n".join(buf))
            except Exception as e:
                print("error:", e)
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


if __name__ == "__main__":
    main()
