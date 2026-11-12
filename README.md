# Search Visualizer

Watch a multistart search explore a generated landscape. Change **Search breadth** to trade longer individual trails for more starting locations. The browser demo draws the terrain layer by layer, colours the crawler paths, and marks the lowest point found so far.

## Run locally

From the repository root, start the browser demo with Python 3.

```sh
python -m http.server 8000 --bind 127.0.0.1 --directory web
```

Open [the browser demo on localhost](http://127.0.0.1:8000/). Choosing a breadth starts a new run. Pause, replay, or drag the timeline to compare routes at the same move. Reduced-motion mode opens on the completed map.

For the Python desktop view, run `python search-vis.py` with Tk installed. For a repeatable result in the terminal, run `python search-vis.py --headless --breadth wide`. Add `--csv` to write the terrain and the visit counts.

## Compare the search

All three settings use the Tourmaline seed on a 128 × 128 grid. Each run takes 500 initial samples, spends 4,000 moves branching, 1,000 refining, and 100 on the final route. A move counts one proposed neighbour, including repeat visits. The preset determines the number of logical crawlers and their route length. No CPU thread configuration is required.

| Search breadth | Starting locations promoted | Branching crawlers | Moves per branching crawler |
| --- | ---: | ---: | ---: |
| Focused | 1 | 2 | 2,000 |
| Balanced | 4 | 8 | 500 |
| Wide | 16 | 32 | 125 |

Balanced reproduces the branch allocation of David Hampson's 2017 search. On this seed, all three finish at the terrain minimum, approximately −15.74465 at (37, 11). Compare the trails midway through a run to see how they get there.

## Finish report

Coverage is the percentage of grid cells visited at the start of at least one move, where the crawler records its current score. Revisiting a cell adds no coverage. The denominator includes all 16,384 cells. For example, Balanced visits 1,629 distinct cells in 5,600 moves, giving 9.9% coverage. The optimality gap is the best recorded score minus the true minimum over the entire unsmoothed terrain, in objective-score units. Equal scores give an exact match, including a tie at another coordinate. Reproduce the example with `python search-vis.py --headless --breadth balanced` or finish a Balanced run in the browser.
