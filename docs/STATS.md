# Dataset statistics

Output of `python scripts/stats.py`. Re-run the script and paste the output here whenever the data files change.

```
Total triples: 6733

Individuals per class
class     individuals
--------  -----------
Movie     250
Person    672
Director  156
Actor     522
Genre     17
Studio    99
Country   16

owl:sameAs links per target
target        movies  people  total
------------  ------  ------  -----
wikidata.org  249     671     920
dbpedia.org   249     667     916

Movies per genre
genre            movies
---------------  ------
Drama            82
Adventure        36
Action           29
Comedy           16
Crime            16
Science Fiction  14
Animation        13
Fantasy          11
Horror           9
Thriller         7
Romance          4
Western          4
Mystery          3
War              3
Family           1
History          1
Music            1

Top 5 directors by number of movies
director           movies
-----------------  ------
Steven Spielberg   8
Christopher Nolan  7
Quentin Tarantino  7
David Fincher      6
Martin Scorsese    6
```
