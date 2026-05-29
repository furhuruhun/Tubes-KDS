import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator
import numpy as np

try:
    import seaborn as sns
    _HAS_SNS = True
except ImportError:
    _HAS_SNS = False

# Sentralisasi variabel warna ke objek kamus tunggal
PALETTE = {
    "bg":          "#0D1B2A", 
    "panel":       "#132338", 
    "grid":        "#1E3450", 
    "text":        "#E8F0F7", 
    "subtext":     "#7FA8C9", 
    "accent":      "#38BDF8", 
    "karbohidrat": "#F4A460", 
    "protein":     "#38BDF8", 
    "lipid":       "#82EFAC", 
    "esensial":    "#F472B6", 
    "non_esensial": "#60A5FA", 
    "border":      "#2C4A6B", 
}

ESSENTIAL_AMINO_ACIDS = frozenset({
    "histidin", "isoleusin", "leusin", "lisin",
    "metionin", "fenilalanin", "treonin", "triptofan", "valin",
})

MACRO_LABELS = {"karbohidrat": "Karbohidrat", "protein": "Protein", "lipid": "Lipid"}
DPI = 300
FONT_FAM = "DejaVu Sans"


def _apply_dark_style() -> None:
    """Mengatur gaya visual dasar memanfaatkan kamus PALETTE."""
    plt.rcParams.update({
        "figure.facecolor":     PALETTE["bg"],
        "axes.facecolor":       PALETTE["panel"],
        "axes.edgecolor":       PALETTE["border"],
        "axes.labelcolor":      PALETTE["text"],
        "axes.titlecolor":      PALETTE["text"],
        "xtick.color":          PALETTE["subtext"],
        "ytick.color":          PALETTE["subtext"],
        "text.color":           PALETTE["text"],
        "grid.color":           PALETTE["grid"],
        "font.family":          FONT_FAM,
        "figure.dpi":           DPI,
        "savefig.dpi":          DPI,
    })


def _styled_spine(ax: plt.Axes, sides: tuple = ("bottom", "left")) -> None:
    """Mengatur kemunculan garis tepi plot tertentu agar minimalis."""
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(side in sides)
        if side in sides:
            ax.spines[side].set_color(PALETTE["border"])


def _watermark(fig: plt.Figure, label: str = "Pemodelan Energi Makromolekul") -> None:
    """Menambahkan teks metadata kecil di sudut bawah grafik."""
    fig.text(0.99, 0.01, label, ha="right", va="bottom", fontsize=7, color=PALETTE["border"], style="italic")


def plot_calorie_distribution(data: dict, save_path: Path):
    _apply_dark_style()
    rasio = data.get("rasio_kalori", {})
    energi = data.get("energi", {})
    detail = data.get("klasifikasi_diet", {}).get("detail", {})
    
    labels_raw = ["karbohidrat", "protein", "lipid"]
    sizes = [rasio.get(f"{k}_ratio", 0) * 100 for k in labels_raw]
    colors = [PALETTE[k] for k in labels_raw]
    explode = [0.06 if detail.get(k, {}).get("status") != "normal" else 0.02 for k in labels_raw]

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(sizes, explode=explode, colors=colors, autopct="%1.1f%%", startangle=90, textprops=dict(color=PALETTE["bg"], fontweight="bold"))
    ax.add_artist(plt.Circle((0, 0), 0.55, fc=PALETTE["bg"]))
    
    ax.text(0, 0, f"{energi.get('total_kcal', 0):.0f}\nkkal", ha="center", va="center", color=PALETTE["text"], fontsize=13, fontweight="bold")
    _watermark(fig)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_atp_comparison(data: dict, save_path: Path):
    _apply_dark_style()
    energi = data.get("energi", {})
    atp = data.get("atp", {})
    
    categories = ["Karbohidrat", "Lipid", "Protein"]
    kcal_vals = [energi.get("karbohidrat_kcal", 0), energi.get("lipid_kcal", 0), energi.get("protein_kcal", 0)]
    atp_vals = [atp.get("karbohidrat_atp", 0), atp.get("lipid_atp", 0), atp.get("protein_atp", 0)]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    x = np.arange(len(categories))
    
    ax1.bar(x, kcal_vals, 0.45, color=PALETTE["karbohidrat"])
    ax1.set_title("Nilai Energi Nutrisi")
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    _styled_spine(ax1)
    
    ax2.bar(x, atp_vals, 0.45, color=PALETTE["protein"])
    ax2.set_title("Estimasi Hasil ATP")
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories)
    _styled_spine(ax2)
    
    _watermark(fig)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_amino_acid_profile(data: dict, save_path: Path):
    aa_breakdown = data.get("breakdown_asam_amino")
    if not aa_breakdown: return
    _apply_dark_style()
    sorted_aa = sorted(aa_breakdown.items(), key=lambda item: item[1])
    names = [k.capitalize() for k, _ in sorted_aa]
    grams = [v for _, v in sorted_aa]
    colors = [PALETTE["esensial"] if k.lower() in ESSENTIAL_AMINO_ACIDS else PALETTE["non_esensial"] for k, _ in sorted_aa]
    
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.barh(names, grams, color=colors, height=0.6)
    ax.set_title("Profil Berat Komposisi Asam Amino")
    _styled_spine(ax)
    _watermark(fig)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_atp_per_amino_acid(data: dict, save_path: Path):
    atp_detail = data.get("atp_detail_per_aa")
    if not atp_detail: return
    _apply_dark_style()
    per_aa = atp_detail.get("atp_per_asam_amino", {})
    sorted_atp = sorted(per_aa.items(), key=lambda item: item[1], reverse=True)
    names = [k.capitalize() for k, _ in sorted_atp]
    values = [v for _, v in sorted_atp]
    
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(names, values, color=PALETTE["protein"], width=0.6)
    ax.axhline(np.mean(values), color=PALETTE["esensial"], linestyle="--", alpha=0.7)
    ax.set_title("Kontribusi Energi Spesifik per Asam Amino")
    _styled_spine(ax)
    _watermark(fig)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def visualize_all(export_dict: dict, save_dir: str = "plots"):
    out_path = Path(save_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    plot_calorie_distribution(export_dict, out_path / "calorie_distribution.png")
    plot_atp_comparison(export_dict, out_path / "atp_comparison.png")
    if "breakdown_asam_amino" in export_dict:
        plot_amino_acid_profile(export_dict, out_path / "amino_acid_profile.png")
    if "atp_detail_per_aa" in export_dict:
        plot_atp_per_amino_acid(export_dict, out_path / "atp_detail_per_amino_acid.png")


if __name__ == "__main__":
    DEMO_DATA = {
        "metadata": {"timestamp": "2026-05-29T12:00:00", "versi": "1.0"},
        "input": {"karbohidrat_g": 220.0, "protein_g": 75.0, "lipid_g": 55.0},
        "energi": {"total_kcal": 1675.0, "karbohidrat_kcal": 880.0, "lipid_kcal": 495.0, "protein_kcal": 300.0},
        "rasio_kalori": {"karbohidrat_ratio": 0.52, "lipid_ratio": 0.29, "protein_ratio": 0.19},
        "atp": {"karbohidrat_atp": 46.4, "lipid_atp": 27.7, "protein_atp": 37.5, "total_atp": 111.6, "metode": "rata-rata per gram"},
        "klasifikasi_diet": {"label": "Balanced", "detail": {}},
        "breakdown_asam_amino": {"leusin": 5.6, "lisin": 6.6, "valin": 3.6, "isoleusin": 3.7},
        "atp_detail_per_aa": {"atp_per_asam_amino": {"leusin": 1.4, "lisin": 1.5, "valin": 0.7}, "total_atp": 3.6, "metode": "Akurat"}
    }
    visualize_all(DEMO_DATA)