# Surf zone lab: group tasks

**The question for the whole class:** a storm sea reaches the coast. What does it turn into before the shoreline, and how high does the water get on land?

Each group changes **one thing** and keeps everything else as it is in the notebook. Together, the groups build the full picture.

## How every group works

You run `Base_case.ipynb` **once per case** in your table, then compare.

1. In **01**, set `CASE_NAME` and the values from the first row of your table. Leave everything else as it is.
2. Look at the profile figure. Is it what you expected?
3. Fill in your **prediction** before running (cell before **03**). Don't skip this.
4. Run **02**, **03** and **04**. While SWASH runs (a few minutes), discuss what you expect in the next case.
5. Go back to **01**: next row of your table (new name, new value), and run again down to **04**.
6. When all your cases are done, go to **06**, put your case names in `CASES`, and compare.
7. Prepare your **3-minute presentation** (end of this page).

The notebook starts with: `WAVE = "jonswap"`, `Hs = 2.5`, `Tp = 10`, `WL = 0.0`, `PROFILE = "beach"`, `m = 1/30`, `bar_height = 0`.

---

## Group A: Regular or irregular waves?

| `CASE_NAME` | Change |
|---|---|
| `"A_mono"` | `WAVE = "mono"` |
| `"A_jonswap"` | `WAVE = "jonswap"` |

**Question:** both seas carry the same energy. Does the coast notice the difference?

Look at: the IG panel, `IG/Hss` and `Ru2`. Compare the "waves in time" plots of both cases.

---

## Group B: Bigger waves

| `CASE_NAME` | Change |
|---|---|
| `"B_Hs1"` | `Hs = 1` |
| `"B_Hs2_5"` | `Hs = 2.5` |
| `"B_Hs4"` | `Hs = 4` |

**Question:** if the waves offshore are four times higher, what is four times bigger at the shoreline, and what is not?

Look at: where breaking starts, `Hss` at h = 1 m, `IG/Hss`, and the setup compared with `Hs`.

---

## Group C: Longer waves

| `CASE_NAME` | Change |
|---|---|
| `"C_Tp7"` | `Tp = 7` |
| `"C_Tp10"` | `Tp = 10` |
| `"C_Tp14"` | `Tp = 14` |

**Question:** same height, longer period. What changes in the surf zone, and what changes on the beach?

Look at: `Hss` at h = 1 m, `IG` at h = 1 m, and `Ru2`.

---

## Group D: Steeper beach

| `CASE_NAME` | Change |
|---|---|
| `"D_m30"` | `m = 1/30` |
| `"D_m20"` | `m = 1/20` |
| `"D_m15"` | `m = 1/15` |

**Question:** what does a steeper beach change in the surf zone, and on the beach?

Look at: the width of the surf zone, `IG/Hss`, `Ru2`, and the "waves in time" plots near the shoreline.

---

## Group E: A sandbar

| `CASE_NAME` | Change |
|---|---|
| `"E_nobar"` | `bar_height = 0` |
| `"E_bar1_5"` | `bar_height = 1.5` |
| `"E_bar2_5"` | `bar_height = 2.5` |

**Question:** does a sandbar protect the beach behind it?

Look at: where the waves break, what happens to `Hss` between the bar and the shore, the IG panel, and `Ru2`.

---

## Group F: Tide on a coral reef

| `CASE_NAME` | Change |
|---|---|
| `"F_WLm1"` | `PROFILE = "reef"` and `WL = -1` |
| `"F_WL0"` | `PROFILE = "reef"` and `WL = 0` |
| `"F_WLp1"` | `PROFILE = "reef"` and `WL = 1` |

**Question:** the same storm arrives at low, mid or high tide. How does the water depth on the reef control what reaches the beach?

Look at: `Hss` on the reef flat, the setup, `Ru2` and **`Ru2 + WL`**. Which one tells you about flooding?

---

## Extra (if you finish early)

**Rough reef:** `PROFILE = "reef"`, and `reef_n = 0.01`, `0.1` and `0.2` (names `"X_n001"`, `"X_n01"`, `"X_n02"`). Which waves does friction remove the most?

Or test your own explanation with values you haven't tried. Predict first, then run.

---

## Your 3-minute presentation

Show **one figure** (from step 06) and answer:

1. What did you predict, and where were you right or wrong?
2. Which number changed the most, and which barely changed?
3. **Why?** Use one of: wave breaking, setup, wave groups and long (IG) waves, reflection, friction.
4. One sentence for a coastal engineer: what should they remember from your result?

Then fill in your row of the class table on the board:

| Increase... | x_break moves | Hss, h = 1 m | IG, h = 1 m | Setup | Ru2 | Ru2 + WL |
|---|---|---|---|---|---|---|
| A: irregular instead of regular | | | | | | |
| B: Hs | | | | | | |
| C: Tp | | | | | | |
| D: beach slope | | | | | | |
| E: bar height | | | | | | |
| F: water level on the reef | | | | | | |

Use ↑, ↓ or =, and for x_break write *offshore* or *onshore*.
