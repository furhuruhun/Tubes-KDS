import json
import sys
import os
import textwrap
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
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

BG_COLOR = "#0D1B2A"      
TEXT_COLOR = "#E0E1DD"    
MUTED_COLOR = "#8D99AE"   
ACCENT_PRIMARY = "#1B4965" 
ACCENT_SECONDARY = "#62B6CB" 
ALERT_COLOR = "#D90429"   

ESSENTIAL_AMINO_ACIDS = frozenset({
    "histidin", "isoleusin", "leusin", "lisin",
    "metionin", "fenilalanin", "treonin", "triptofan", "valin",
})


def _apply_dark_style():
    plt.rcParams.update({
        "figure.facecolor": BG_COLOR,
        "axes.facecolor": BG_COLOR,
        "text.color": TEXT_COLOR,
        "axes.labelcolor": TEXT_COLOR,
        "xtick.color": MUTED_COLOR,
        "ytick.color": MUTED_COLOR,
        "axes.edgecolor": ACCENT_PRIMARY,
        "grid.color": ACCENT_PRIMARY,
        "grid.alpha": 0.3,
        "font.family": "sans-serif",
        "figure.dpi": 300
    })


def plot_calorie_distribution(data: dict, save_path: Path):
    _apply_dark_style()
    rasio = data.get("rasio_kalori", {})
    energi = data.get("energi", {})
    diet_detail = data.get("klasifikasi_diet", {}).get("detail", {})
    
    labels = ["Karbohidrat", "Lipid", "Protein"]
    values = [rasio.get("karbohidrat_ratio", 0), rasio.get("lipid_ratio", 0), rasio.get("protein_ratio", 0)]
    if sum(values) == 0: return

    colors = [ACCENT_PRIMARY, ACCENT_SECONDARY, MUTED_COLOR]
    explode = [0.06 if diet_detail.get(k, {}).get("status") != "normal" else 0.0 for k in ["karbohidrat", "lipid", "protein"]]

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(values, explode=explode, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90, textprops=dict(color=TEXT_COLOR))
    fig.gca().add_artist(plt.Circle((0, 0), 0.55, fc=BG_COLOR))
    
    ax.text(0, 0, f"{energi.get('total_kcal', 0):.0f}\nkkal", ha="center", va="center", color=TEXT_COLOR, fontsize=12, fontweight="bold")
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
    
    ax1.bar(x, kcal_vals, 0.45, color=ACCENT_PRIMARY)
    ax1.set_title("Nilai Energi Nutrisi (kkal)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    
    ax2.bar(x, atp_vals, 0.45, color=ACCENT_SECONDARY)
    ax2.set_title("Estimasi Hasil ATP (mol)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories)
    
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
    
    colors = [ACCENT_SECONDARY if k.lower() in ESSENTIAL_AMINO_ACIDS else ACCENT_PRIMARY for k, _ in sorted_aa]
    
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.barh(names, grams, color=colors, height=0.6)
    ax.set_title("Profil Berat Komposisi Asam Amino")
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
    ax.bar(names, values, color=ACCENT_PRIMARY, width=0.6)
    ax.axhline(np.mean(values), color=ALERT_COLOR, linestyle="--", alpha=0.7)
    ax.set_title("Kontribusi Energi Spesifik per Asam Amino")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_dashboard_summary(data: dict, save_path: Path):
    """Menggabungkan komponen utama ke dalam satu lembar panel berkas infografis besar."""
    _apply_dark_style()
    fig = plt.figure(figsize=(12, 8))
    gs = gridspec.GridSpec(2, 2)
    
    # Subplot Mini Kiri: Info
    ax_info = fig.add_subplot(gs[0, 0])
    ax_info.axis("off")
    ax_info.text(0.0, 0.7, f"Klasifikasi Diet: {data.get('klasifikasi_diet', {}).get('label', 'Unclassified')}", fontsize=12, fontweight="bold", color=TEXT_COLOR)
    
    # Subplot Mini Kanan: Pie
    ax_pie = fig.add_subplot(gs[0, 1])
    rasio = data.get("rasio_kalori", {})
    ax_pie.pie([rasio.get("karbohidrat_ratio", 0), rasio.get("lipid_ratio", 0), rasio.get("protein_ratio", 0)], colors=[ACCENT_PRIMARY, ACCENT_SECONDARY, MUTED_COLOR])
    ax_pie.set_title("Alokasi Kalori")

    # Subplot Bawah Kiri: Bar ATP
    ax_atp = fig.add_subplot(gs[1, 0])
    atp = data.get("atp", {})
    ax_atp.bar(["Karbo", "Lipid", "Protein"], [atp.get("karbohidrat_atp", 0), atp.get("lipid_atp", 0), atp.get("protein_atp", 0)], color=ACCENT_SECONDARY)
    ax_atp.set_title("Estimasi Output ATP")

    # Subplot Bawah Kanan: AA
    ax_aa = fig.add_subplot(gs[1, 1])
    aa_data = data.get("breakdown_asam_amino", {})
    if aa_data:
        top_aa = sorted(aa_data.items(), key=lambda x: x[1], reverse=True)[:5]
        ax_aa.barh([x[0].capitalize() for x in top_aa], [x[1] for x in top_aa], color=ACCENT_PRIMARY)
    ax_aa.set_title("Kandungan Asam Amino Utama")

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def print_dashboard(data: dict):
    rasio = data.get("rasio_kalori", {})
    print("\n" + "="*50)
    print("         DASHBOARD TEKSTUAL MONITORING ENERGI")
    print("="*50)
    for k, v in rasio.items():
        bar = "█" * int(v * 20) + "░" * (20 - int(v * 20))
        print(f"  {k.split('_')[0].capitalize():<12}: {v*100:5.1f}% [{bar}]")
    print("="*50 + "\n")


def visualize_all(export_dict: dict, save_dir: str = "plots"):
    out_path = Path(save_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    plot_calorie_distribution(export_dict, out_path / "calorie_distribution.png")
    plot_atp_comparison(export_dict, out_path / "atp_comparison.png")
    if "breakdown_asam_amino" in export_dict:
        plot_amino_acid_profile(export_dict, out_path / "amino_acid_profile.png")
    if "atp_detail_per_aa" in export_dict:
        plot_atp_per_amino_acid(export_dict, out_path / "atp_detail_per_amino_acid.png")
    plot_dashboard_summary(export_dict, out_path / "diet_dashboard.png")
    print_dashboard(export_dict)


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

if __name__ == "__main__":
    visualize_all(DEMO_DATA)