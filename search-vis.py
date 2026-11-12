"""Explore David Hampson's 2017 multistart search on a repeatable terrain."""

import argparse
import csv
import random
from dataclasses import dataclass, field

SIZE = 128
SEED = "Tourmaline"
# Number of starts promoted after scattering, then after branching.
PRESETS = {"focused": (1, 1), "balanced": (4, 2), "wide": (16, 8)}
MOVES = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, 1), (1, -1), (-1, -1)]
ROUTE_COLORS = ("#91d5ff", "#ff8fad", "#63e2bc", "#ffc483", "#dfa5ff", "#bce87d", "#ffa5df", "#b7c7ff")
STAGES = ("Scatter", "Branch", "Refine", "Finish")


def make_terrain(rng):
    def plane():
        return [[0.0] * SIZE for _ in range(SIZE)]

    a, b, c, d = (plane() for _ in range(4))
    for x in range(SIZE):
        for y in range(SIZE):
            previous = a[x][y-1] if x == 0 else (
                a[x-1][y-1] + a[x-1][y] + a[x-1][(y+1) % SIZE]
            ) / 3
            a[x][y] = previous + rng.uniform(-10, 10)
    for x in range(SIZE):
        for y in range(SIZE):
            if x == 0:
                previous = b[x][y-1]
            elif y == 0:
                previous = b[x-1][y]
            else:
                previous = (b[x-1][y] + b[x][y-1]) / 2
            b[x][y] = previous + rng.uniform(-10, 10)
    for y in range(SIZE):
        for x in range(SIZE):
            previous = 0 if y == 0 else (
                c[x-1][y-1] + c[x][y-1] + c[(x+1) % SIZE][y-1]
            ) / 3
            c[x][y] = previous + rng.uniform(-10, 10)
    for x in range(SIZE):
        for y in reversed(range(SIZE)):
            if x == 0:
                previous = d[x][(y+1) % SIZE]
            elif y == SIZE-1:
                previous = d[x-1][y]
            else:
                previous = (d[x-1][y] + d[x][y+1]) / 2
            d[x][y] = previous + rng.uniform(-10, 10)
    return [[(a[x][y] + b[x][y] + c[x][y] + d[x][y]) / 4
             for y in range(SIZE)] for x in range(SIZE)]


@dataclass
class Crawler:
    x: int
    y: int
    value: float = 0.0
    path: list = field(default_factory=list)


@dataclass
class Result:
    terrain: list
    visits: list
    stages: list
    best: tuple
    minimum: tuple


def search(breadth):
    rng = random.Random(SEED)
    terrain = make_terrain(rng)
    visits = [[0] * SIZE for _ in range(SIZE)]
    minimum = min((value, x, y) for x, row in enumerate(terrain) for y, value in enumerate(row))
    best = (float("inf"), 0, 0)

    def advance(crawlers, greed, rounds):
        nonlocal best
        for crawler in crawlers:
            crawler.path.append((crawler.x, crawler.y))
        for _ in range(rounds):
            for crawler in crawlers:
                x, y = crawler.x, crawler.y
                crawler.value = terrain[x][y]
                visits[x][y] += 1
                if crawler.value < best[0]:
                    best = (crawler.value, x, y)
                dx, dy = rng.choice(MOVES)
                # Preserve the random draw consumed by list repetition in 2017.
                rng.randint(1, 50)
                nx = max(0, min(SIZE-1, x + dx))
                ny = max(0, min(SIZE-1, y + dy))
                delta = terrain[nx][ny] - crawler.value
                # Keep the original algorithm's uphill acceptance rule.
                if delta < 0 or 2.71828 ** (-delta / greed) < rng.random():
                    crawler.x, crawler.y = nx, ny
                crawler.path.append((crawler.x, crawler.y))
        return crawlers

    def children(crawlers, top, copies):
        return [Crawler(c.x, c.y) for c in sorted(crawlers, key=lambda c: c.value)[:top]
                for _ in range(copies)]

    starts, finalists = PRESETS[breadth]
    scatter = advance([Crawler(rng.randrange(SIZE), rng.randrange(SIZE)) for _ in range(500)], 100, 1)
    branch = advance(children(scatter, starts, 2), 4, 4000 // (2 * starts))
    refine = advance(children(branch, finalists, 1), 10, 1000 // finalists)
    finish = advance(children(refine, 1, 1), 1000, 100)
    return Result(terrain, visits, [scatter, branch, refine, finish], best, minimum)


def writeToFile(result):
    """Export terrain values and visit counts in the original x-major layout."""
    for filename, rows in (("search_domain.csv", result.terrain), ("searched.csv", result.visits)):
        with open(filename, "w", newline="") as output:
            csv.writer(output).writerows(rows)


def describe(result):
    visits = sum(map(sum, result.visits))
    distinct = sum(count > 0 for row in result.visits for count in row)
    best, x, y = result.best
    minimum, mx, my = result.minimum
    return (f"{visits:,} visits | {distinct:,} distinct cells | Best {best:.4f} at ({x}, {y}) | "
            f"Terrain minimum {minimum:.4f} at ({mx}, {my})")


def display(initial):
    import tkinter as tk
    from tkinter import ttk

    window = tk.Tk()
    window.title("Search Visualizer")
    window.configure(background="#101e23")
    unit = max(2, min(5, (window.winfo_screenheight() - 190) // SIZE,
                      (window.winfo_screenwidth() - 70) // SIZE))
    span = SIZE * unit
    bar = ttk.Frame(window, padding=8)
    bar.pack(fill="x")
    ttk.Label(bar, text="Search breadth").pack(side="left")
    breadth = tk.StringVar(value=initial.title())
    menu = ttk.Combobox(bar, textvariable=breadth, values=[p.title() for p in PRESETS],
                        state="readonly", width=10)
    menu.pack(side="left", padx=8)
    stage_label = ttk.Label(bar)
    stage_label.pack(side="right")
    canvas = tk.Canvas(window, width=span, height=span, highlightthickness=0)
    canvas.pack()
    status = tk.StringVar()
    tk.Label(window, textvariable=status, bg="#101e23", fg="#e8f3ed",
             wraplength=span, pady=8).pack()
    tk.Label(window, text="◇ Terrain minimum     ● Best visited", bg="#101e23",
             fg="#e8f3ed", pady=3).pack()
    pending = None
    image = None

    def pixel(point):
        return tuple((coord + 0.5) * unit for coord in point)

    def draw_run(*_):
        nonlocal pending, image
        if pending is not None:
            window.after_cancel(pending)
            pending = None
        result = search(breadth.get().lower())
        canvas.delete("all")
        if image is None:
            lo = result.minimum[0]
            hi = max(map(max, result.terrain))
            palette = []
            for level in range(25):
                fraction = level / 24
                rgb = [round(a + (b-a)*fraction) for a, b in zip((12, 37, 46), (99, 148, 139))]
                palette.append("#%02x%02x%02x" % tuple(rgb))
            base = tk.PhotoImage(width=SIZE, height=SIZE)
            rows = ["{" + " ".join(palette[round((result.terrain[x][y]-lo)/(hi-lo)*24)]
                                  for x in range(SIZE)) + "}" for y in range(SIZE)]
            base.put(" ".join(rows))
            image = base.zoom(unit)
        canvas.create_image(0, 0, image=image, anchor="nw")
        status.set("Tourmaline   ·   128 × 128   ·   5,600 visits")
        stage_label.configure(text="Scatter")
        for crawler in result.stages[0]:
            x, y = pixel(crawler.path[0])
            canvas.create_oval(x-1, y-1, x+1, y+1, fill="#a7bdb7", outline="")

        def animate(stage, start):
            nonlocal pending
            crawlers = result.stages[stage]
            stage_label.configure(text=STAGES[stage])
            end = min(start + max(1, 100 // len(crawlers)), len(crawlers[0].path)-1)
            for lane, crawler in enumerate(crawlers):
                points = [pixel(p) for p in crawler.path[start:end+1]]
                canvas.create_line(*points, fill=ROUTE_COLORS[lane % len(ROUTE_COLORS)] if stage == 1 else ("#ffcf83" if stage == 2 else "#ffffff"), width=2,
                                   capstyle="round", joinstyle="round")
            if end < len(crawlers[0].path)-1:
                pending = window.after(28, animate, stage, end)
            elif stage < 3:
                pending = window.after(120, animate, stage+1, 0)
            else:
                pending = None
                x, y = pixel(result.minimum[1:])
                canvas.create_polygon(x, y-8, x+8, y, x, y+8, x-8, y,
                                      fill="", outline="#ffffff", width=2)
                x, y = pixel(result.best[1:])
                canvas.create_oval(x-4, y-4, x+4, y+4, fill="#ffda7f", outline="#1a282c")
                stage_label.configure(text="Complete")
                status.set(describe(result))
        pending = window.after(200, animate, 1, 0)

    ttk.Button(bar, text="Replay", command=draw_run).pack(side="left")
    menu.bind("<<ComboboxSelected>>", draw_run)
    draw_run()
    window.mainloop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--breadth", choices=PRESETS, default="balanced", help="initial search breadth")
    parser.add_argument("--headless", action="store_true", help="print the completed run without opening a window")
    parser.add_argument("--csv", action="store_true", help="write search_domain.csv and searched.csv")
    args = parser.parse_args()
    if args.headless or args.csv:
        result = search(args.breadth)
        print(describe(result))
        if args.csv:
            writeToFile(result)
    else:
        display(args.breadth)


if __name__ == "__main__":
    main()
