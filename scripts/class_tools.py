"""Tools for the surf-zone class notebook.

Students only pick an experiment and read figures. Everything else lives here:
the experiment definitions, the runs, the measurements and the plots.

Three things differ on purpose from notebooks 01-04:

* The warmup is removed before any statistic is computed. Otherwise the slow
  rise of the mean water level during spin-up is counted as infragravity energy.
* The regular wave has the same energy as the irregular one (H = Hs / sqrt(2)),
  so both start from the same Hss and can be compared directly.
* Quantities are only read on wet cells. SWASH reports the bed level on dry
  cells, so a raw mean water level would climb the beach.

Watlev and Runlev are measured from the still water level set with WL, not from
the profile datum. Add WL to compare with the bed.
"""

import os
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import animation
from scipy.ndimage import uniform_filter1d
from scipy.signal import welch

if not hasattr(np, "trapz"):  # removed from recent NumPy, still used by BlueMath
    np.trapz = np.trapezoid

from bluemath_tk.wrappers.swash.swash_wrapper import SwashModelWrapper

from scripts.bathymetry import linear_profile, reef_profile

REPO = Path(__file__).resolve().parents[1]
TEMPLATES = REPO / "templates" / "templates_class"
OUTPUT = REPO / "cases" / "class"
PRECOMPUTED = REPO / "precomputed"

G = 9.81
WARMUP = 300  # s, removed from all statistics
COMPTIME = 900  # s, long enough for several IG waves
INCIDENT_LIMIT = 25.0  # s, periods above this count as infragravity
WET_DEPTH = 0.05  # m, shallower cells are treated as dry

COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"
SAND = "#e9dcc3"
DRY = "#d8d7d2"

BEACH = {"h0": -12, "Ltotal": 1000, "Wfore": 400}
REEF = {
    "dx": 1,
    "h0": 15,
    "Slope1": 0.05,
    "Slope2": 0.1,
    "Wreef": 200,
    "Wfore": 500,
    "bCrest": 10,
    "emsl": 2.5,
}
REEF_FLAT = (800, 1000)  # m, where the roughness experiment acts

BASE_CASE = {"wave": "irregular", "Hs": 2.5, "Tp": 10.0, "WL": 0.0, "m": 10 / 300, "n": 0.01}

EXPERIMENTS = {
    "REF": {
        "title": "Reference: regular vs irregular waves, same energy",
        "profile": "beach",
        "cases": [{"wave": "regular"}, {"wave": "irregular"}],
    },
    "A": {"title": "Wave height", "profile": "beach", "lever": "Hs", "values": [1.0, 2.5, 4.0]},
    "B": {"title": "Wave period", "profile": "beach", "lever": "Tp", "values": [7.0, 10.0, 14.0]},
    "C": {"title": "Beach slope", "profile": "beach", "lever": "m", "values": [0.033, 0.05, 0.067]},
    "D": {"title": "Water level on a reef", "profile": "reef", "lever": "WL", "values": [-1.0, 0.0, 1.0]},
    "E": {"title": "Reef roughness", "profile": "reef", "lever": "n", "values": [0.02, 0.10, 0.20]},
    "CHALLENGE": {
        "title": "Which one floods more?",
        "profile": "reef",
        "cases": [
            {"Hs": 3.5, "Tp": 8.0, "WL": -1.0},
            {"Hs": 2.0, "Tp": 14.0, "WL": 1.0},
        ],
    },
}

UNITS = {"Hs": "m", "Tp": "s", "WL": "m", "m": "", "n": ""}


# ---------------------------------------------------------------- experiment setup


def bed_elevation(profile, m=None):
    """Return x and bed elevation z (m, positive up) for a profile."""
    if profile == "beach":
        return linear_profile(
            h0=BEACH["h0"], Ltotal=BEACH["Ltotal"], Wconst=BEACH["Wfore"], slope=m
        )
    return reef_profile(**REEF)


def experiment_cases(key, values=None):
    """Return the full parameter dict of every case in an experiment."""
    spec = EXPERIMENTS[key]
    if "cases" in spec:
        changes = spec["cases"]
    else:
        changes = [{spec["lever"]: v} for v in (values or spec["values"])]
    cases = [{**BASE_CASE, **c} for c in changes]
    for case in cases:
        _check_case(case, spec["profile"])
    return cases


def _check_case(case, profile):
    if case["Tp"] >= INCIDENT_LIMIT:
        raise ValueError(f"Tp must stay below {INCIDENT_LIMIT:.0f} s, or it counts as IG.")
    if profile == "beach":
        crest = BEACH["h0"] + case["m"] * (BEACH["Ltotal"] - BEACH["Wfore"])
        if crest - case["WL"] < 3:
            raise ValueError(
                f"Slope m={case['m']:.3f} leaves the beach top only {crest:.1f} m high. "
                "Use m >= 0.025 on this 600 m beach."
            )
    steepness = case["Hs"] / (G * case["Tp"] ** 2 / (2 * np.pi))
    if not 0.005 <= steepness <= 0.05:
        print(f"Note: Hs/L0 = {steepness:.4f} is outside the usual 0.005-0.05 range.")


class ClassSwashWrapper(SwashModelWrapper):
    """SWASH wrapper with per-case bed and friction, and warmup removed."""

    def __init__(self, profile, **kwargs):
        self.profile = profile
        super().__init__(**kwargs)

    def build_case(self, case_context, case_dir):
        _, z = bed_elevation(self.profile, case_context.get("m"))
        self.depth_array = -z
        case_context["H_regular"] = case_context["Hs"] / np.sqrt(2)
        super().build_case(case_context=case_context, case_dir=case_dir)
        np.savetxt(os.path.join(case_dir, "depth.bot"), self.depth_array)

        friction = np.full(len(self.depth_array), BASE_CASE["n"])
        friction[REEF_FLAT[0] : REEF_FLAT[1]] = case_context["n"]
        np.savetxt(os.path.join(case_dir, "friction.txt"), friction)

    def _convert_case_output_files_to_nc(self, case_num, output_path, run_path):
        ds = super()._convert_case_output_files_to_nc(case_num, output_path, run_path)
        return ds.sel(Tsec=slice(self.fixed_parameters["warmup"], None))


# ---------------------------------------------------------------- run and load


@dataclass
class Experiment:
    key: str
    title: str
    cases: list  # one xarray.Dataset per case

    @property
    def labels(self):
        return [c.attrs["label"] for c in self.cases]


def _label(key, case):
    spec = EXPERIMENTS[key]
    if key == "REF":
        return f"{case['wave']} waves"
    if "lever" in spec:
        lever = spec["lever"]
        return f"{lever} = {case[lever]:g} {UNITS[lever]}".strip()
    return f"Hs {case['Hs']:g} m, Tp {case['Tp']:g} s, WL {case['WL']:+g} m"


def _check_stable(key, i, label, water):
    """SWASH can blow up and still exit normally, so look at the water level."""
    if np.isnan(water).any():
        first = int(np.flatnonzero(np.isnan(water).any(axis=0))[0])
        print(
            f"WARNING {key} case {i} ({label}): the model became unstable about {first} s "
            "into the record. Do not use this case. Change a value slightly and rerun, "
            f"or use load_experiment('{key}')."
        )


def _compact_case(key, params, profile, post, output_nc):
    """Keep what the class uses, in one small file per case."""
    x, z = bed_elevation(profile, params["m"])
    n = len(z)
    water = output_nc["Watlev"].squeeze(drop=True).transpose("Xp", "Tsec")
    _check_stable(key, params.get("index", 0), _label(key, params), water.values)
    ds = xr.Dataset(
        {
            "Watlev": (("x", "t"), water.values[:n]),
            "Runlev": (("t",), output_nc["Runlev"].values),
            "Hss": (("x",), post["Hss"].values[:n]),
            "ig": (("x",), post["ig"].values[:n]),
            "Msetup": (("x",), post["Msetup"].values[:n]),
            "z": (("x",), z),
        },
        coords={"x": x, "t": output_nc["Tsec"].values},
        attrs={**params, "Ru2": float(post["Ru2"].values), "label": _label(key, params),
               "profile": profile},
    )
    return ds


def run_experiment(key, values=None, launcher=None, num_workers=None):
    """Run one experiment with SWASH and return an Experiment."""
    spec = EXPERIMENTS[key]
    params = experiment_cases(key, values)
    frame = pd.DataFrame(params)
    frame["Hs_L0"] = 2 * np.pi * frame["Hs"] / (G * frame["Tp"] ** 2)

    wrapper = ClassSwashWrapper(
        profile=spec["profile"],
        templates_dir=str(TEMPLATES),
        metamodel_parameters=frame.drop(columns="Tp").to_dict(orient="list"),
        fixed_parameters={
            "dxinp": 1,
            "comptime": COMPTIME,
            "warmup": WARMUP,
            "n_nodes_per_wavelength": 60,
        },
        output_dir=str(OUTPUT / key),
        depth_array=-bed_elevation(spec["profile"], params[0]["m"])[1],
        debug=False,
    )
    wrapper.build_cases()
    launcher = launcher or os.environ.get("SWASH_LAUNCHER", "serial")
    if num_workers:
        wrapper.run_cases(launcher=launcher, num_workers=num_workers)
    else:
        wrapper.run_cases(launcher=launcher)
    post = wrapper.postprocess_cases(output_vars=["Msetup", "Hfreqs", "Ru2"])
    if post.sizes["case_num"] != len(params):
        raise RuntimeError(
            f"A case in {key} failed, most likely a numerical blow-up. Try slightly different "
            f"values, or use load_experiment('{key}') to carry on with stored results."
        )

    cases = []
    for i, case in enumerate(params):
        with xr.open_dataset(OUTPUT / key / f"{i:04}" / "output.nc") as output_nc:
            compact = _compact_case(
                key, {**case, "index": i}, spec["profile"], post.isel(case_num=i), output_nc.load()
            )
        cases.append(compact)
    return Experiment(key, spec["title"], cases)


def save_precomputed(experiment, folder=PRECOMPUTED):
    """Store an experiment so the class can load it without running SWASH."""
    target = Path(folder) / experiment.key
    target.mkdir(parents=True, exist_ok=True)
    level = {"dtype": "int16", "scale_factor": 0.001, "_FillValue": -32768, "zlib": True}
    for i, case in enumerate(experiment.cases):
        case.to_netcdf(target / f"case_{i}.nc", encoding={"Watlev": level, "Runlev": level})


def load_experiment(key, folder=PRECOMPUTED):
    """Load a stored experiment. Same result as run_experiment, no SWASH needed."""
    files = sorted((Path(folder) / key).glob("case_*.nc"))
    if not files:
        raise FileNotFoundError(f"No stored results for {key} in {folder}.")
    cases = []
    for path in files:
        with xr.open_dataset(path) as ds:
            cases.append(ds.load())
    return Experiment(key, EXPERIMENTS[key]["title"], cases)


# ---------------------------------------------------------------- measurements


def wet_mask(case):
    """True from offshore up to the mean shoreline."""
    depth = (case["Msetup"] + case.attrs["WL"] - case["z"]).values
    dry = np.flatnonzero(depth < WET_DEPTH)
    shore = dry[0] if len(dry) else len(depth)
    return np.arange(len(depth)) < shore


def _swash_heights(case):
    """Swash height (4 std) split into incident and infragravity bands."""
    runup = case["Runlev"].values
    dt = float(np.median(np.diff(case["t"].values)))
    f, spectrum = welch(runup - runup.mean(), fs=1 / dt, nperseg=256, nfft=512)
    df = f[1] - f[0]
    limit = 1 / INCIDENT_LIMIT
    return (
        4 * np.sqrt(spectrum[f >= limit].sum() * df),
        4 * np.sqrt(spectrum[f < limit].sum() * df),
    )


def measure(case):
    """Return the standard measurements of one case."""
    wet = wet_mask(case)
    wl = case.attrs["WL"]
    x = case["x"].values
    z = case["z"].values
    mean_level = case["Msetup"].values
    depth = mean_level + wl - z
    hss = case["Hss"].values

    # 31 m window, longer than the partial standing pattern from beach reflection.
    # Breaking is where Hss has lost 10% of its peak: robust for random waves,
    # whose peak is flat and can sit far offshore for large Hs.
    smooth = uniform_filter1d(hss, 31, mode="nearest")
    i_break = int(np.flatnonzero(wet & (smooth >= 0.9 * smooth[wet].max()))[-1])
    i_still = int(np.flatnonzero(z >= wl)[0])
    shoreward = np.flatnonzero(wet & (np.arange(len(x)) >= i_break) & (depth <= 1.0))
    i_inner = int(shoreward[0]) if len(shoreward) else int(np.flatnonzero(wet)[-1])
    swash_incident, swash_ig = _swash_heights(case)

    profile = case.attrs["profile"]
    l0 = G * case.attrs["Tp"] ** 2 / (2 * np.pi)
    slope = case.attrs["m"] if profile == "beach" else REEF["Slope1"]

    return {
        "case": case.attrs["label"],
        "Iribarren": slope / np.sqrt(case.attrs["Hs"] / l0),
        "x_break (m)": x[i_break],
        "Hss/h at break": smooth[i_break] / depth[i_break],
        "Hss, h=1 m (m)": hss[i_inner],
        "IG, h=1 m (m)": case["ig"].values[i_inner],
        "IG/Hss": case["ig"].values[i_inner] / hss[i_inner],
        "Setup at still-water line (m)": mean_level[i_still],
        "Mean shoreline level (m)": case["Runlev"].values.mean(),
        "Swash, incident (m)": swash_incident,
        "Swash, IG (m)": swash_ig,
        "Ru2 above still water (m)": case.attrs["Ru2"],
        "Ru2 + WL (m)": case.attrs["Ru2"] + wl,
    }


def summary(experiment):
    """Return the measurement table of an experiment, one row per case."""
    table = pd.DataFrame([measure(c) for c in experiment.cases]).set_index("case")
    return table.round(2)


# ---------------------------------------------------------------- figures


def _style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, length=0, labelsize=9)
    ax.yaxis.label.set_color(MUTED)
    ax.xaxis.label.set_color(MUTED)


def _x_limits(experiment):
    shore = max(c["x"].values[wet_mask(c)][-1] for c in experiment.cases)
    start = 300 if experiment.cases[0].attrs["profile"] == "beach" else 500
    return start, shore + 30


def plot_profiles(experiment):
    """Standard figure: Hss, IG and setup across the profile, plus the bed."""
    fig, axes = plt.subplots(
        4, 1, figsize=(10, 9), sharex=True, height_ratios=[3, 3, 3, 2], facecolor=SURFACE
    )
    for i, case in enumerate(experiment.cases):
        wet = wet_mask(case)
        x = case["x"].values[wet]
        color = COLORS[i]
        style = dict(lw=2, color=color, label=case.attrs["label"])
        axes[0].plot(x, case["Hss"].values[wet], **style)
        axes[1].plot(x, case["ig"].values[wet], **style)
        axes[2].plot(x, case["Msetup"].values[wet], **style)
        axes[3].plot(case["x"], case["z"], lw=2, color=color)
        axes[3].plot(x, np.full(x.size, case.attrs["WL"]), lw=1, ls="--", color=color)

    axes[0].set_ylabel("Hss (m)\nincident waves")
    axes[1].set_ylabel("IG height (m)\nperiods > 25 s")
    axes[2].set_ylabel("Mean level (m)\nabove still water")
    axes[3].set_ylabel("Bed (m)\ndashed: still water")
    axes[3].set_xlabel("Cross-shore distance (m)")
    axes[0].set_ylim(bottom=0)
    axes[1].set_ylim(bottom=0)
    axes[2].axhline(0, color=MUTED, lw=0.8)
    axes[3].set_ylim(top=6)
    axes[0].set_xlim(*_x_limits(experiment))
    for ax in axes:
        _style(ax)
    fig.suptitle(experiment.title, x=0.07, ha="left", fontsize=14, color=INK)
    axes[0].legend(frameon=False, ncol=3, loc="lower left", bbox_to_anchor=(0, 1.0),
                   labelcolor=INK, fontsize=10)
    fig.tight_layout()
    plt.show()


def plot_xt(experiment, case=0, seconds=300):
    """Space-time plot: all motions next to periods above 25 s only."""
    ds = experiment.cases[case]
    wet = wet_mask(ds)
    x = ds["x"].values[wet]
    t = ds["t"].values
    level = ds["Watlev"].values[wet, :]
    anomaly = level - level.mean(axis=1, keepdims=True)
    window = int(round(INCIDENT_LIMIT / np.median(np.diff(t))))
    slow = uniform_filter1d(anomaly, window, axis=1, mode="nearest")
    keep = (t >= t[0] + window) & (t <= t[0] + window + seconds)  # skip the filter edge

    fig, axes = plt.subplots(1, 2, figsize=(11, 6), sharey=True, sharex=True, facecolor=SURFACE)
    for ax, field, title in zip(
        axes, (anomaly, slow), ("All motions: short waves and bores", "Periods above 25 s: IG waves")
    ):
        limit = max(float(np.percentile(np.abs(field[:, keep]), 99.5)), 0.05)
        mesh = ax.pcolormesh(x, t[keep], field[:, keep].T, cmap="RdBu_r", vmin=-limit, vmax=limit,
                             shading="auto", rasterized=True)
        colorbar = fig.colorbar(mesh, ax=ax, pad=0.02, shrink=0.8)
        colorbar.set_label("Level above the local mean (m)", color=MUTED, fontsize=9)
        colorbar.outline.set_visible(False)
        colorbar.ax.tick_params(colors=MUTED, length=0, labelsize=8)
        ax.set_title(title, loc="left", color=INK, fontsize=11)
        ax.set_xlabel("Cross-shore distance (m)")
        _style(ax)
        ax.grid(False)
        ax.set_xlim(_x_limits(experiment)[0], x[-1])
    axes[0].set_ylabel("Time (s)")
    fig.suptitle(ds.attrs["label"], x=0.07, ha="left", fontsize=14, color=INK)
    fig.tight_layout()
    plt.show()


def animate(experiment, case=0, seconds=150):
    """Return an HTML animation of the water surface."""
    from IPython.display import HTML

    ds = experiment.cases[case]
    x = ds["x"].values
    z = ds["z"].values
    surface = ds["Watlev"].values + ds.attrs["WL"]
    level = np.where(surface - z[:, None] > 0.005, surface, np.nan)
    frames = int(min(seconds, level.shape[1]))
    start, stop = _x_limits(experiment)

    fig, ax = plt.subplots(figsize=(9, 3.6), dpi=80, facecolor=SURFACE)
    ax.fill_between(x, z, z.min() - 1, color=SAND, zorder=1)
    ax.plot(x, z, color=MUTED, lw=1.5, zorder=2)
    line, = ax.plot(x, level[:, 0], color=COLORS[0], lw=2, zorder=3)
    title = ax.set_title("", loc="left", color=INK, fontsize=11)
    ax.set_xlim(start, stop)
    ax.set_ylim(max(z.min() - 1, -14), np.nanmax(level[:, :frames]) + 0.5)
    ax.set_xlabel("Cross-shore distance (m)")
    ax.set_ylabel("Elevation (m)")
    _style(ax)

    def update(frame):
        line.set_ydata(level[:, frame])
        title.set_text(f"{ds.attrs['label']}, t = {ds['t'].values[frame]:.0f} s")
        return line, title

    ani = animation.FuncAnimation(fig, update, frames=frames, interval=120, blit=True)
    plt.close(fig)
    return HTML(ani.to_jshtml())


# ---------------------------------------------------------------- notebook helpers


def preview(key, values=None):
    """Show the cases of an experiment before running it."""
    rows = []
    for case in experiment_cases(key, values):
        l0 = G * case["Tp"] ** 2 / (2 * np.pi)
        on_beach = EXPERIMENTS[key]["profile"] == "beach"
        rows.append(
            {
                "wave": case["wave"],
                "Hs (m)": case["Hs"],
                "Tp (s)": case["Tp"],
                "WL (m)": case["WL"],
                "slope": round(case["m"], 3) if on_beach else REEF["Slope1"],
                "Manning n": case["n"],
                "Hs/L0": round(case["Hs"] / l0, 4),
            }
        )
    return pd.DataFrame(rows)


def class_table(keys=("A", "B", "C", "D", "E")):
    """Join the stored results of all groups, for the teach-back."""
    tables = {key: summary(load_experiment(key)) for key in keys}
    return pd.concat(tables, names=["group", "case"])
