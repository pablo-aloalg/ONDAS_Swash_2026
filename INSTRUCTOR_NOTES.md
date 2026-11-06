# Instructor notes: Surf_zone_class.ipynb

Not for students: this file contains the answers.

## Timetable (120 min)

| Min | Activity | Notebook section |
|---|---|---|
| 0–10 | The question, and a paper sketch of `Hss`, `IG` and mean level | 0 |
| 10–35 | Read the reference case together | 1 |
| 35–75 | Group experiments: predict, run, explain | 2 |
| 75–80 | Break | |
| 80–105 | Presentations, 3 min each, then the class table | 3 |
| 105–120 | Vote on the challenge, reveal, exit question | 4 and 5 |

Groups of 2–3. If you have more than five groups, repeat a letter.

## Results to expect

Stored runs, 900 s after a 300 s warmup. Students who run the same cases on the class machine should get close to these, but see "Before class".

**Reference, 1:30 beach, Hs 2.5 m, Tp 10 s**

| | Regular | Irregular |
|---|---|---|
| IG at h = 1 m (m) | 0.01 | 0.95 |
| Hss at h = 1 m (m) | 0.89 | 0.92 |
| Setup at still-water line (m) | 0.35 | 0.36 |
| Swash, IG band (m) | 0.02 | 1.90 |
| Ru2 above still water (m) | 0.54 | 2.23 |

The main message: same energy, same `Hss` and same still-water setup, but four times the runup, because of wave groups.

**A, wave height** (`Hs` = 1, 2.5, 4 m)

| | 1 | 2.5 | 4 |
|---|---|---|---|
| x_break (m) | 698 | 638 | 577 |
| Hss at h = 1 m (m) | 0.70 | 0.92 | 1.00 |
| IG at h = 1 m (m) | 0.30 | 0.95 | 1.49 |
| Setup at still-water line (m) | 0.15 | 0.36 | 0.60 |
| Ru2 (m) | 0.99 | 2.23 | 3.32 |

Bring out: the height quadruples but inner surf `Hss` grows by less than half, because it is depth-limited. Setup stays near 0.15 `Hs`. IG takes over: `IG/Hss` goes from 0.43 to 1.49.

**B, wave period** (`Tp` = 7, 10, 14 s)

| | 7 | 10 | 14 |
|---|---|---|---|
| Hss at h = 1 m (m) | 0.83 | 0.92 | 0.97 |
| IG at h = 1 m (m) | 0.86 | 0.95 | 1.61 |
| Setup at still-water line (m) | 0.29 | 0.36 | 0.50 |
| Swash, incident (m) | 0.31 | 0.27 | 0.28 |
| Swash, IG (m) | 1.61 | 1.90 | 3.04 |
| Ru2 (m) | 1.66 | 2.23 | 2.95 |

Bring out: `Hss` barely changes while runup nearly doubles. Incident swash is flat, so the increase is all in the IG band.

**C, beach slope** (`m` = 0.033, 0.05, 0.067)

| | 0.033 | 0.05 | 0.067 |
|---|---|---|---|
| Iribarren | 0.26 | 0.40 | 0.53 |
| x_break (m) | 641 | 560 | 523 |
| Mean shoreline level (m) | 0.89 | 0.87 | 0.95 |
| Swash, incident (m) | 0.27 | 0.62 | 1.06 |
| Swash, IG (m) | 1.90 | 2.26 | 2.60 |
| Ru2 (m) | 2.27 | 2.56 | 2.70 |

Bring out: setup barely responds, but incident swash almost quadruples. On the mild slope incident swash is saturated, and on the steeper slope more of it reaches the shore. Iribarren organises this.

**D, reef water level** (`WL` = −1, 0, +1 m)

| | −1 | 0 | +1 |
|---|---|---|---|
| Hss at h = 1 m (m) | 0.72 | 1.19 | 1.50 |
| IG at h = 1 m (m) | 0.92 | 1.01 | 1.12 |
| Setup at still-water line (m) | 0.31 | 0.34 | 0.40 |
| Ru2 above still water (m) | 1.90 | 2.01 | 2.39 |
| Ru2 + WL (m) | 0.90 | 2.01 | 3.39 |

Bring out: 2 m of water level adds 2.5 m to the flood level, because deeper water over the reef lets more incident energy through.

**E, reef roughness** (`n` = 0.02, 0.1, 0.2)

| | 0.02 | 0.1 | 0.2 |
|---|---|---|---|
| Hss at h = 1 m (m) | 1.18 | 1.04 | 0.65 |
| IG at h = 1 m (m) | 1.01 | 0.67 | 0.34 |
| Setup at still-water line (m) | 0.34 | 0.29 | 0.22 |
| Swash, IG (m) | 1.50 | 1.05 | 0.51 |
| Ru2 (m) | 2.03 | 1.75 | 1.02 |

Bring out: breaking on the reef edge does not change (`x_break` stays at 768 m). Friction acts on what crosses the flat, and it removes IG the most. Runup halves.

**Challenge**

| | Hs 3.5 m, Tp 8 s, WL −1 m | Hs 2 m, Tp 14 s, WL +1 m |
|---|---|---|
| Ru2 above still water (m) | 2.16 | 2.34 |
| Ru2 + WL (m) | 1.16 | 3.34 |

The runup itself is nearly the same, but the smaller, longer swell at high water reaches about 2 m higher. If a student reads the wrong column, the question "Which column answers the question about flooding?" is the discussion.

## Points students may raise

- **The regular `Hss` wiggles.** The beach reflects part of the regular wave, which makes a partial standing pattern. This is why `x_break` uses a smoothed `Hss`.
- **Runup is only in the IG band on the 1:30 beach.** These runs are 1D with normal incidence, which tends to exaggerate IG compared with a real, directionally spread sea. Treat the pattern as the lesson. For the class, the results are taken as truth.
- **`Ru2` jumps a little between similar cases.** About 90 waves in 900 s means 2% is only a few uprushes. Trends are meaningful, small differences are not.
- **Mean shoreline level is above the still-water setup.** The first is the mean height of the moving shoreline. The second is the mean level at a fixed point.

## What changed from notebooks 01–04

- **Warmup removed before all statistics.** In the old notebooks it creates false IG near the shore.
- **`comptime` raised from 300 to 900 s** so the IG band has enough record.
- **Regular wave uses H = Hs / √2** so both wave types carry the same energy.
- **`SET DEPMIN= 0.01` and `TIMEI 0.05 0.3` in the class template.** With the previous settings, SWASH 10.05 blew up on the base reef case and on Hs = 4 m. The water level went to NaN and SWASH still finished normally.
- **Friction outside the reef flat is n = 0.01**, not 0 as in notebook 04.
- **A stability check warns students** if a run contains NaN.
- **`pytz` added to `requirements.txt`.** A fresh install fails without it.

## Before class

1. **Run the notebook in the class environment**, at least groups D and A. The stored results and the stability testing used SWASH 10.05 on Windows, and the class image had SWASH 11.01 last year. The `geoocean/rocky8` image itself has not been tested.
2. **Regenerate the stored results there if the numbers differ noticeably.** Use `exp = ct.run_experiment(key)`, then `ct.save_precomputed(exp)`, for `REF`, `A`–`E` and `CHALLENGE`.
3. **Time one reef case.** I expect roughly 1.5–3 min per case on last year's machine, based on its logs and the stricter time step. That is not measured.
4. **Don't push `INSTRUCTOR_NOTES.md` to a repo students can read.** The `precomputed/` folder also holds the results.
