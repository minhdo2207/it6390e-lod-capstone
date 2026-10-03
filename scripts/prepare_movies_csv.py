"""Build the cleaned movies CSV from the Kaggle "TMDB 5000 Movie Dataset".

Usage:
    python prepare_movies_csv.py <tmdb_5000_movies.csv> <tmdb_5000_credits.csv> <output.csv>

Selection: movies with at least MIN_VOTES votes, top LIMIT by average rating.
Rows missing a title, release date or director are dropped.

Output columns:
    id, title, year, release_date, runtime, director_id, director_name,
    genre, genres, cast_ids, cast_names, studio, country

`genre`, `studio` and `country` hold the first listed value (TMDB lists the
primary one first). `genres`, `cast_ids` and `cast_names` are "|"-separated;
cast is limited to the TOP_CAST first-billed actors.
"""

import csv
import json
import sys

MIN_VOTES = 1000
LIMIT = 250
TOP_CAST = 3

FIELDS = [
    "id", "title", "year", "release_date", "runtime",
    "director_id", "director_name",
    "genre", "genres", "cast_ids", "cast_names", "studio", "country",
]


def names(json_text):
    return [item["name"].strip() for item in json.loads(json_text or "[]")]


def build_rows(movies, credits_by_id):
    rows = []
    for movie in movies:
        credits = credits_by_id.get(movie["id"])
        if not credits or not movie["title"] or not movie["release_date"]:
            continue

        directors = [p for p in json.loads(credits["crew"]) if p["job"] == "Director"]
        if not directors:
            continue

        cast = sorted(json.loads(credits["cast"]), key=lambda p: p["order"])[:TOP_CAST]
        genres = names(movie["genres"])
        studios = names(movie["production_companies"])
        countries = names(movie["production_countries"])

        rows.append({
            "id": movie["id"],
            "title": movie["title"].strip(),
            "year": movie["release_date"][:4],
            "release_date": movie["release_date"],
            "runtime": movie["runtime"].split(".")[0],
            "director_id": directors[0]["id"],
            "director_name": directors[0]["name"].strip(),
            "genre": genres[0] if genres else "",
            "genres": "|".join(genres),
            "cast_ids": "|".join(str(p["id"]) for p in cast),
            "cast_names": "|".join(p["name"].strip() for p in cast),
            "studio": studios[0] if studios else "",
            "country": countries[0] if countries else "",
        })
    return rows


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    movies_path, credits_path, output_path = sys.argv[1:]
    csv.field_size_limit(sys.maxsize)  # the cast/crew JSON cells are very large

    with open(movies_path, encoding="utf-8") as f:
        movies = [m for m in csv.DictReader(f) if int(m["vote_count"]) >= MIN_VOTES]
    with open(credits_path, encoding="utf-8") as f:
        credits_by_id = {row["movie_id"]: row for row in csv.DictReader(f)}

    movies.sort(key=lambda m: (float(m["vote_average"]), int(m["vote_count"])), reverse=True)
    rows = build_rows(movies, credits_by_id)[:LIMIT]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} movies to {output_path}")


if __name__ == "__main__":
    main()
