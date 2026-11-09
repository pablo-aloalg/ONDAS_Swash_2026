"""Save, load, compare and plot SWASH cases run with SwashModelWrapper_ondas.

After a case runs, save_case() writes a small results.nc next to the SWASH
files (cases/<name>/results.nc). Every other function works from case names,
so cases run at different times, or by the teacher, can be compared.

Water levels are measured from the still water level (WL), as SWASH reports them.
"""

import os.path as op
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import animation
from scipy.ndimage import uniform_filter1d

REPO = Path(__file__).resolve().parents[1]
FOLDERS = [REPO / "cases", REPO / "backup_results"]

G = 9.81
WET_DEPTH = 0.05      # m, shallower cells count as dry
IG_PERIOD = 25.0      # s, longer periods count as infragravity
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#8e5bd0", "#c9a227", "#d6457a"]


# ------------------------------------------------------------------ save and load


def save_case(name, postprocessed, x, z, WL, Hs, Tp, wave, output_dir, manning_n=0.01,
              output_data=None):
    """Write cases/<name>/results.nc with what the comparison needs."""
    n = len(z)
    ds = xr.Dataset(
        {
            "z": (("x",), np.asarray(z, float)),
            "Hs": (("x",), postprocessed["Hs"].values[:n]),
            "Hss": (("x",), postprocessed["Hss"].values[:n]),
            "ig": (("x",), postprocessed["ig"].values[:n]),
            "Msetup": (("x",), postprocessed["Msetup"].values[:n]),
        },
        coords={"x": np.asarray(x, float)},
        attrs={"name": name, "WL": float(WL), "Hs_offshore": float(Hs), "Tp": float(Tp),
               "wave": str(wave), "manning_n": float(manning_n),
               "Ru2": float(postprocessed["Ru2"].values)},
    )
    if output_data is not None and "Runlev" in output_data:
        ds["Runlev"] = (("t",), output_data["Runlev"].values.ravel())
        ds = ds.assign_coords(t=output_data["Tsec"].values)
    folder = Path(output_dir) / name
    folder.mkdir(parents=True, exist_ok=True)
    ds.to_netcdf(folder / "results.nc")
    print(f"Saved as '{name}'. Ru2 = {ds.attrs['Ru2']:.2f} m")


def load_case(name):
    """Load a saved case by name, from cases/ or backup_results/."""
    for folder in FOLDERS:
        path = folder / name / "results.nc"
        if path.exists():
            with xr.open_dataset(path) as ds:
                return ds.load()
    raise FileNotFoundError(
        f"No saved case called '{name}'. Check the spelling, and that you ran its "
        "'save' cell after the run."
    )


def saved_cases():
    """Names of every saved case."""
    names = []
    for folder in FOLDERS:
        names += sorted(p.parent.name for p in folder.glob("*/results.nc"))
    return names


# ------------------------------------------------------------------ measurements


def _wet(ds):
    depth = ds["Msetup"].values + ds.attrs["WL"] - ds["z"].values
    dry = np.flatnonzero(depth < WET_DEPTH)
    shore = dry[0] if len(dry) else len(depth)
    return np.arange(len(depth)) < shore


def measure(ds):
    """The standard numbers of one case."""
    wet = _wet(ds)
    WL = ds.attrs["WL"]
    x, z = ds["x"].values, ds["z"].values
    level = ds["Msetup"].values
    depth = level + WL - z
    hss = ds["Hss"].values
    smooth = uniform_filter1d(hss, 31, mode="nearest")
    i_break = int(np.flatnonzero(wet & (smooth >= 0.9 * smooth[wet].max()))[-1])
    i_still = int(np.flatnonzero(z >= WL)[0])
    inner = np.flatnonzero(wet & (np.arange(len(x)) >= i_break) & (depth <= 1.0))
    i_inner = int(inner[0]) if len(inner) else int(np.flatnonzero(wet)[-1])
    return {
        "x_break (m)": x[i_break],
        "Hss/h at break": smooth[i_break] / depth[i_break],
        "Hss, h=1 m (m)": hss[i_inner],
        "IG, h=1 m (m)": ds["ig"].values[i_inner],
        "IG/Hss": ds["ig"].values[i_inner] / hss[i_inner],
        "Setup at shore (m)": level[i_still],
        "Ru2 (m)": ds.attrs["Ru2"],
        "Ru2 + WL (m)": ds.attrs["Ru2"] + WL,
    }


def case_table(names):
    """Table of the standard numbers, one column per case."""
    rows = {}
    for name in names:
        ds = load_case(name)
        a = ds.attrs
        rows[name] = {"wave": a["wave"], "Hs (m)": a["Hs_offshore"], "Tp (s)": a["Tp"],
                      "WL (m)": a["WL"], "Manning n": a.get("manning_n", 0.01), **measure(ds)}
    table = pd.DataFrame(rows)
    return table.apply(lambda col: col.map(lambda v: round(v, 2) if isinstance(v, float) else v))


def trend_table(groups, tolerance=0.10):
    """Class table. groups = {"B: Hs": ["B_Hs1", "B_Hs2.5", "B_Hs4"], ...}.

    Trend from the first case to the last; under 10% (10 m for x_break) is '='.
    """
    keep = ["x_break (m)", "Hss, h=1 m (m)", "IG, h=1 m (m)", "Setup at shore (m)",
            "Ru2 (m)", "Ru2 + WL (m)"]
    out = {}
    for group, names in groups.items():
        a, b = measure(load_case(names[0])), measure(load_case(names[-1]))
        row = {}
        for k in keep:
            if k.startswith("x_break"):
                word = "=" if abs(b[k] - a[k]) < 10 else ("onshore" if b[k] > a[k] else "offshore")
                row[k] = f"{word} ({a[k]:.0f} → {b[k]:.0f})"
            else:
                same = abs(b[k] - a[k]) <= tolerance * max(abs(a[k]), abs(b[k]), 0.05)
                word = "=" if same else ("↑" if b[k] > a[k] else "↓")
                row[k] = f"{word} ({a[k]:.2f} → {b[k]:.2f})"
        out[group] = row
    return pd.DataFrame(out).T


# ------------------------------------------------------------------ figures


def plot_results(names, title=None):
    """Hss, IG, mean level and bed along the profile, for one or more saved cases."""
    if isinstance(names, str):
        names = [names]
    fig, axes = plt.subplots(4, 1, figsize=(11, 10), sharex=True, height_ratios=[3, 3, 3, 2])
    start, end = np.inf, 0
    for i, name in enumerate(names):
        ds = load_case(name)
        wet = _wet(ds)
        x = ds["x"].values
        color = COLORS[i % len(COLORS)]
        axes[0].plot(x[wet], ds["Hss"].values[wet], color=color, lw=2, label=name)
        axes[1].plot(x[wet], ds["ig"].values[wet], color=color, lw=2)
        axes[2].plot(x[wet], ds["Msetup"].values[wet], color=color, lw=2)
        axes[3].plot(x, ds["z"].values, color=color, lw=2)
        axes[3].plot(x[wet], np.full(wet.sum(), ds.attrs["WL"]), color=color, lw=1, ls="--")
        deep = np.flatnonzero(ds.attrs["WL"] - ds["z"].values >= 3 * ds.attrs["Hs_offshore"])
        start = min(start, max(deep[-1] - 100, 0) if len(deep) else 0)
        end = max(end, x[wet][-1] + 30)

    axes[0].set_ylabel("Hss (m)\nshort waves")
    axes[1].set_ylabel("IG (m)\nlong waves, T > 25 s")
    axes[2].set_ylabel("Mean level (m)\nabove still water")
    axes[3].set_ylabel("Bed (m)\ndashed: still water")
    axes[3].set_xlabel("Cross-shore distance (m)")
    axes[0].set_ylim(bottom=0)
    axes[1].set_ylim(bottom=0)
    axes[2].axhline(0, color="gray", lw=0.8)
    axes[3].set_ylim(top=6)
    axes[0].set_xlim(start, end)
    for ax in axes:
        ax.grid(True, ls="--", alpha=0.4)
    axes[0].legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, frameon=False)
    if title:
        fig.suptitle(title, fontsize=14)
    plt.tight_layout()
    plt.show()


def _surface(output_data, z, WL):
    """Water level (from still water) on wet cells, as (x, t), NaN where dry."""
    level = output_data["Watlev"].squeeze(drop=True)
    level = level.transpose("Xp", "Tsec").values[: len(z)]
    depth = level + WL - np.asarray(z)[:, None]
    return np.where(depth > WET_DEPTH, level, np.nan), output_data["Tsec"].values


def plot_xt(output_data, x, z, WL, seconds=300):
    """Space-time plot: all motions, and only the long (IG) waves."""
    level, t = _surface(output_data, z, WL)
    keep_x = ~np.isnan(level).all(axis=1)
    keep_x &= np.asarray(WL - np.asarray(z) < 15)  # skip the deep, flat part
    level = np.where(keep_x[:, None], level, 0.0)
    anomaly = np.nan_to_num(level - np.nanmean(level, axis=1, keepdims=True))
    window = int(round(IG_PERIOD / np.median(np.diff(t))))
    slow = uniform_filter1d(anomaly, window, axis=1, mode="nearest")
    keep_t = (t >= t[0] + window) & (t <= t[0] + window + seconds)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True)
    for ax, field, name in zip(axes, (anomaly, slow),
                               ("All waves", "Long waves only (periods > 25 s)")):
        part = field[keep_x][:, keep_t]
        lim = max(float(np.percentile(np.abs(part), 99.5)), 0.05)
        mesh = ax.pcolormesh(np.asarray(x)[keep_x], t[keep_t], part.T, cmap="RdBu_r",
                             vmin=-lim, vmax=lim, shading="auto", rasterized=True)
        fig.colorbar(mesh, ax=ax, label="Water level above its mean (m)")
        ax.set_title(name)
        ax.set_xlabel("Cross-shore distance (m)")
    axes[0].set_ylabel("Time (s)")
    plt.tight_layout()
    plt.show()


def animate_case(output_data, x, z, WL, seconds=150):
    """Animation of the water surface. Only `seconds` of record, to keep it light."""
    from IPython.display import HTML

    level, t = _surface(output_data, z, WL)
    surface = level + WL
    dt = float(np.median(np.diff(t)))
    frames = min(int(seconds / dt), surface.shape[1])
    x, z = np.asarray(x), np.asarray(z)
    deep = np.flatnonzero(WL - z >= 15)
    start = x[deep[-1]] if len(deep) else x[0]
    wet = np.flatnonzero(~np.isnan(level).all(axis=1))
    end = x[wet[-1]] + 50 if len(wet) else x[-1]

    fig, ax = plt.subplots(figsize=(10, 4), dpi=80)
    ax.fill_between(x, z, z.min() - 1, color="navajowhite", alpha=0.6, zorder=0)
    ax.plot(x, z, color="k", lw=1.5)
    line, = ax.plot(x, surface[:, 0], color="tab:blue", lw=2)
    ax.set_xlim(start, end)
    ax.set_ylim(max(z.min(), WL - 15) - 0.5, np.nanmax(surface[:, :frames]) + 0.5)
    ax.set_xlabel("Cross-shore distance (m)")
    ax.set_ylabel("Elevation (m)")
    ax.grid(True, ls="--", alpha=0.4)
    title = ax.set_title("")

    def update(i):
        line.set_ydata(surface[:, i])
        title.set_text(f"t = {t[i]:.0f} s")
        return line, title

    ani = animation.FuncAnimation(fig, update, frames=frames, interval=100, blit=True)
    plt.close(fig)
    return HTML(ani.to_jshtml())
