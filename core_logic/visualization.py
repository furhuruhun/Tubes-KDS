from __future__ import annotations

import json
import sys
import os
import textwrap
from pathlib import Path
from datetime import datetime
from typing import Optional

import matplotlib
matplotlib.use("Agg") # Non-interactive backend untuk simpan file gambar tanpa pop-up GUI
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

# Palet warna tema akademik deep teal
PALETTE = {
    "bg":          "#0D1B2A", # Latar belakang utama figura
    "panel":       "#132338", # Latar belakang plot axes
    "grid":        "#1E3450", # Garis bantu/grid
    "text":        "#E8F0F7", # Teks utama
    "subtext":     "#7FA8C9", # Label sekunder dan teks sumbu
    "accent":      "#38BDF8", # Warna sorotan biru langit
    "karbohidrat": "#F4A460", # Jingga pasir
    "protein":     "#38BDF8", # Biru muda
    "lipid":       "#82EFAC", # Hijau mint
    "esensial":    "#F472B6", # Merah muda/rose
    "non_esensial": "#60A5FA", # Biru periwinkle
    "border":      "#2C4A6B", # Batas/garis tepi plot
}

ESSENTIAL_AMINO_ACIDS = frozenset({
    "histidin", "isoleusin", "leusin", "lisin",
    "metionin", "fenilalanin", "treonin", "triptofan", "valin",
})

MACRO_LABELS = {
    "karbohidrat": "Karbohidrat",
    "protein":     "Protein",
    "lipid":       "Lipid",
}

DPI = 300
FONT_FAM = "DejaVu Sans"


def _apply_dark_style() -> None:
    """Mengatur gaya gelap visual dasar grafik Matplotlib."""
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
        "grid.linewidth":       0.6,
        "grid.linestyle":       "--",
        "legend.facecolor":     PALETTE["panel"],
        "legend.edgecolor":     PALETTE["border"],
        "legend.labelcolor":    PALETTE["text"],
        "font.family":          FONT_FAM,
        "font.size":            10,
        "axes.titlesize":       13,
        "axes.titleweight":     "bold",
        "axes.labelsize":       10,
        "figure.dpi":           DPI,
        "savefig.dpi":          DPI,
        "savefig.bbox":         "tight",
        "savefig.facecolor":    PALETTE["bg"],
    })


def _styled_spine(ax: plt.Axes, sides: tuple = ("bottom", "left")) -> None:
    """Mengatur kemunculan garis tepi plot tertentu."""
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(side in sides)
        if side in sides:
            ax.spines[side].set_color(PALETTE["border"])
            ax.spines[side].set_linewidth(0.8)


def _watermark(fig: plt.Figure, label: str = "Pemodelan Energi Makromolekul") -> None:
    """Menambahkan teks keterangan kecil di pojok bawah grafik."""
    fig.text(
        0.99, 0.01, label,
        ha="right", va="bottom",
        fontsize=7, color=PALETTE["border"],
        style="italic",
    )


def plot_calorie_distribution(
    rasio_kalori: dict,
    energi: dict,
    klasifikasi_diet: dict,
    save_path: Optional[Path] = None,
) -> plt.Figure:
    """Membuat pie chart (donut chart) untuk persentase distribusi energi makronutrien."""
    _apply_dark_style()

    labels_raw = ["karbohidrat", "protein", "lipid"]
    sizes = [rasio_kalori[f"{k}_ratio"] * 100 for k in labels_raw]
    labels = [MACRO_LABELS[k] for k in labels_raw]
    colors = [PALETTE[k] for k in labels_raw]

    detail = klasifikasi_diet.get("detail", {})
    explode = []
    for k in labels_raw:
        status = detail.get(k, {}).get("status", "normal")
        explode.append(0.06 if status != "normal" else 0.02)

    fig, ax = plt.subplots(figsize=(7, 6))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,
        colors=colors,
        explode=explode,
        autopct="%1.1f%%",
        pctdistance=0.72,
        startangle=90,
        wedgeprops=dict(linewidth=1.4, edgecolor=PALETTE["bg"]),
        shadow=False,
    )
    for at in autotexts:
        at.set_color(PALETTE["bg"])
        at.set_fontsize(11)
        at.set_fontweight("bold")

    for i, k in enumerate(labels_raw):
        status = detail.get(k, {}).get("status", "normal")
        if status != "normal":
            wedges[i].set_linewidth(2.5)
            wedges[i].set_edgecolor(PALETTE["accent"])

    diet_label = klasifikasi_diet.get("label", "—")
    sesuai_rda = klasifikasi_diet.get("sesuai_rda", False)
    rda_text = "✓ Sesuai RDA" if sesuai_rda else "✗ Di Luar RDA"
    rda_color = PALETTE["lipid"] if sesuai_rda else PALETTE["esensial"]

    ax.text(0, 0, f"{energi['total_kcal']:.0f}\nkkal",
            ha="center", va="center", fontsize=15, fontweight="bold",
            color=PALETTE["text"])

    legend_handles = []
    for i, k in enumerate(labels_raw):
        kcal = energi[f"{k}_kcal"]
        stat = detail.get(k, {}).get("status", "normal")
        sym = "↑" if stat == "tinggi" else ("↓" if stat == "rendah" else "✓")
        legend_handles.append(
            mpatches.Patch(color=colors[i],
                           label=f"{labels[i]}  {sizes[i]:.1f}%  ({kcal:.0f} kkal) {sym}")
        )
    ax.legend(handles=legend_handles, loc="lower center",
              bbox_to_anchor=(0.5, -0.12), ncol=1,
              frameon=True, fontsize=9)

    title_str = f"Distribusi Kalori Makronutrien\nDiet: {diet_label} | {rda_text}"
    ax.set_title(title_str, pad=18, color=PALETTE["text"], fontsize=12)
    ax.title.set_color(PALETTE["text"])

    fig.text(0.5, 0.01, rda_text, ha="center", fontsize=9,
             color=rda_color, fontweight="bold")

    _watermark(fig)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path)
    return fig


def plot_atp_comparison(
    atp: dict,
    energi: dict,
    save_path: Optional[Path] = None,
) -> plt.Figure:
    """Membuat perbandingan diagram batang horizontal berdampingan antara ATP dan Kalori Nutrisi."""
    _apply_dark_style()

    macros = ["karbohidrat", "protein", "lipid"]
    labels = [MACRO_LABELS[m] for m in macros]
    atp_vals = [atp[f"{m}_atp"] for m in macros]
    kcal_vals = [energi[f"{m}_kcal"] for m in macros]
    colors = [PALETTE[m] for m in macros]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    fig.patch.set_facecolor(PALETTE["bg"])

    y = np.arange(len(labels))
    bar_h = 0.55

    bars1 = ax1.barh(y, atp_vals, height=bar_h, color=colors, linewidth=0, zorder=3)
    ax1.set_facecolor(PALETTE["panel"])
    ax1.set_xlabel("mol ATP", fontsize=10)
    ax1.set_title("Estimasi ATP per Makronutrien", fontsize=11, pad=10)
    ax1.set_yticks(y)
    ax1.set_yticklabels(labels, fontsize=10)
    ax1.xaxis.set_major_locator(MaxNLocator(integer=False, nbins=5))
    ax1.grid(axis="x", zorder=0)
    _styled_spine(ax1, ("bottom", "left"))

    for bar, val in zip(bars1, atp_vals):
        ax1.text(bar.get_width() * 0.96, bar.get_y() + bar.get_height() / 2,
                 f"{val:.2f}", ha="right", va="center",
                 color=PALETTE["bg"], fontsize=9, fontweight="bold")

    ax1.axvline(atp["total_atp"], color=PALETTE["accent"], linestyle=":", linewidth=1.2, alpha=0.6)
    ax1.text(atp["total_atp"], len(labels) - 0.1,
             f"Total: {atp['total_atp']:.2f}", color=PALETTE["accent"],
             fontsize=8, ha="center")

    bars2 = ax2.barh(y, kcal_vals, height=bar_h, color=colors, linewidth=0, zorder=3)
    ax2.set_facecolor(PALETTE["panel"])
    ax2.set_xlabel("kkal", fontsize=10)
    ax2.set_title("Energi per Makronutrien (Atwater)", fontsize=11, pad=10)
    ax2.set_yticks(y)
    ax2.set_yticklabels(labels, fontsize=10)
    ax2.xaxis.set_major_locator(MaxNLocator(integer=False, nbins=5))
    ax2.grid(axis="x", zorder=0)
    _styled_spine(ax2, ("bottom", "left"))

    for bar, val in zip(bars2, kcal_vals):
        ax2.text(bar.get_width() * 0.96, bar.get_y() + bar.get_height() / 2,
                 f"{val:.0f}", ha="right", va="center",
                 color=PALETTE["bg"], fontsize=9, fontweight="bold")

    ax2.axvline(energi["total_kcal"], color=PALETTE["accent"], linestyle=":", linewidth=1.2, alpha=0.6)
    ax2.text(energi["total_kcal"], len(labels) - 0.1,
             f"Total: {energi['total_kcal']:.0f}", color=PALETTE["accent"],
             fontsize=8, ha="center")

    handles = [mpatches.Patch(color=PALETTE[m], label=MACRO_LABELS[m]) for m in macros]
    fig.legend(handles=handles, loc="lower center", ncol=3,
               frameon=True, fontsize=9, bbox_to_anchor=(0.5, -0.05))

    _watermark(fig)
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    if save_path:
        fig.savefig(save_path)
    return fig


def plot_amino_acid_profile(
    aa_breakdown: dict,
    protein_source: str = "sumber protein",
    save_path: Optional[Path] = None,
) -> plt.Figure:
    """Membuat diagram batang horizontal profil asam amino dan pengelompokan jenis esensialnya."""
    _apply_dark_style()

    aa_items = [(aa, g) for aa, g in aa_breakdown.items() if g > 0]
    aa_items.sort(key=lambda x: x[1], reverse=True)
    if not aa_items:
        return None

    names = [aa.capitalize() for aa, _ in aa_items]
    grams = [g for _, g in aa_items]
    raw_names = [aa for aa, _ in aa_items]
    colors = [PALETTE["esensial"] if aa in ESSENTIAL_AMINO_ACIDS
              else PALETTE["non_esensial"] for aa in raw_names]

    n = len(names)
    fig_h = max(5, n * 0.42 + 1.2)
    fig, ax = plt.subplots(figsize=(9, fig_h))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["panel"])

    y = np.arange(n)
    bars = ax.barh(y, grams, height=0.65, color=colors, linewidth=0, zorder=3)

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel("Gram", fontsize=10)
    ax.set_title(
        f"Profil Asam Amino - {protein_source.replace('_', ' ').title()}\n"
        f"(Total {len(aa_items)} asam amino)",
        fontsize=11, pad=12,
    )
    ax.grid(axis="x", zorder=0)
    _styled_spine(ax, ("bottom", "left"))

    x_max = max(grams)
    for bar, val in zip(bars, grams):
        offset = x_max * 0.01
        ax.text(bar.get_width() + offset,
                bar.get_y() + bar.get_height() / 2,
                f"{val:.4f} g", va="center", ha="left",
                fontsize=7.5, color=PALETTE["subtext"])

    ax.set_xlim(0, x_max * 1.22)

    leg_handles = [
        mpatches.Patch(color=PALETTE["esensial"],    label="Esensial"),
        mpatches.Patch(color=PALETTE["non_esensial"], label="Non-Esensial"),
    ]
    ax.legend(handles=leg_handles, loc="lower right", fontsize=9, frameon=True)

    _watermark(fig)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path)
    return fig


def plot_atp_per_amino_acid(
    atp_detail: dict,
    save_path: Optional[Path] = None,
) -> plt.Figure:
    """Membuat grafik kontribusi mol ATP spesifik komponen asam amino penyusun protein."""
    _apply_dark_style()

    per_aa = atp_detail.get("atp_per_asam_amino", {})
    if not per_aa:
        return None

    sorted_aa = sorted(per_aa.items(), key=lambda x: x[1], reverse=True)
    names = [aa.capitalize() for aa, _ in sorted_aa]
    vals = [v for _, v in sorted_aa]
    raw_names = [aa for aa, _ in sorted_aa]

    colors = [PALETTE["esensial"] if aa in ESSENTIAL_AMINO_ACIDS
              else PALETTE["non_esensial"] for aa in raw_names]

    fig, ax = plt.subplots(figsize=(11, 5))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["panel"])

    x = np.arange(len(names))
    bars = ax.bar(x, vals, width=0.65, color=colors, linewidth=0, zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=38, ha="right", fontsize=8.5)
    ax.set_ylabel("mol ATP", fontsize=10)
    ax.set_title(
        f"Kontribusi ATP per Asam Amino\n"
        f"Total: {atp_detail['total_atp']:.4f} mol ATP | "
        f"Metode: {atp_detail['metode']}",
        fontsize=11, pad=12,
    )
    ax.grid(axis="y", zorder=0)
    _styled_spine(ax, ("bottom", "left"))

    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(vals) * 0.01,
                f"{val:.4f}", ha="center", va="bottom",
                fontsize=7, color=PALETTE["subtext"])

    mean_atp = np.mean(vals)
    ax.axhline(mean_atp, color=PALETTE["accent"], linestyle="--", linewidth=1, alpha=0.7, zorder=4)
    ax.text(len(names) - 0.5, mean_atp + max(vals) * 0.015,
            f"Rata-rata: {mean_atp:.4f}", color=PALETTE["accent"],
            fontsize=8, ha="right")

    leg_handles = [
        mpatches.Patch(color=PALETTE["esensial"],    label="AA Esensial"),
        mpatches.Patch(color=PALETTE["non_esensial"], label="AA Non-Esensial"),
    ]
    ax.legend(handles=leg_handles, loc="upper right", fontsize=9, frameon=True)

    _watermark(fig)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path)
    return fig


def plot_dashboard_summary(
    export_dict: dict,
    save_path: Optional[Path] = None,
) -> plt.Figure:
    """Menggabungkan semua komponen data kuantitatif ke dalam satu lembar panel besar infografis."""
    _apply_dark_style()

    energi = export_dict["energi"]
    rasio = export_dict["rasio_kalori"]
    atp = export_dict["atp"]
    diet = export_dict["klasifikasi_diet"]
    inp = export_dict.get("input", {})
    meta = export_dict.get("metadata", {})

    fig = plt.figure(figsize=(13, 7))
    fig.patch.set_facecolor(PALETTE["bg"])

    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.55, wspace=0.38,
                           left=0.05, right=0.97, top=0.88, bottom=0.06)

    fig.suptitle(
        "RINGKASAN ANALISIS | Pemodelan Komputasi Ekivalen Energi Makromolekul",
        fontsize=13, fontweight="bold", color=PALETTE["text"], y=0.97,
    )
    sub_ts = meta.get("timestamp", datetime.now().isoformat())[:19]
    fig.text(0.5, 0.925, f"Timestamp: {sub_ts} | Versi: {meta.get('versi','1.0')}",
             ha="center", fontsize=8, color=PALETTE["subtext"])

    # Panel A: Tabel ringkasan komponen gram input
    ax_a = fig.add_subplot(gs[0, 0])
    ax_a.set_facecolor(PALETTE["panel"])
    ax_a.axis("off")
    ax_a.set_title("Input Gram", fontsize=10, pad=6)

    macros = ["karbohidrat", "protein", "lipid"]
    rows = [[MACRO_LABELS[m], f"{inp.get(f'{m}_g', 0):.1f} g", f"{energi[f'{m}_kcal']:.1f} kkal"] for m in macros]
    rows.append(["Total", "—", f"{energi['total_kcal']:.1f} kkal"])

    tbl = ax_a.table(
        cellText=rows,
        colLabels=["Makro", "Gram", "Energi"],
        loc="center", cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1.1, 1.5)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_facecolor(PALETTE["grid"] if r == 0 else PALETTE["panel"])
        cell.set_edgecolor(PALETTE["border"])
        cell.set_text_props(color=PALETTE["text"])

    # Panel B: Donut chart versi mini
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.set_facecolor(PALETTE["bg"])
    sizes = [rasio[f"{m}_ratio"] * 100 for m in macros]
    colors = [PALETTE[m] for m in macros]
    detail = diet.get("detail", {})
    explode = [0.06 if detail.get(m, {}).get("status", "normal") != "normal" else 0.02 for m in macros]
    ax_b.pie(sizes, colors=colors, explode=explode,
             autopct="%1.0f%%", pctdistance=0.7, startangle=90,
             wedgeprops=dict(linewidth=1.2, edgecolor=PALETTE["bg"]),
             textprops=dict(color=PALETTE["bg"], fontsize=9, fontweight="bold"))
    ax_b.set_title("Rasio Kalori", fontsize=10, pad=6)

    # Panel C: Grafik ringkasan ATP makro harian
    ax_c = fig.add_subplot(gs[0, 2])
    ax_c.set_facecolor(PALETTE["panel"])
    atp_vals = [atp[f"{m}_atp"] for m in macros]
    y = np.arange(len(macros))
    ax_c.barh(y, atp_vals, height=0.55, color=[PALETTE[m] for m in macros], linewidth=0, zorder=3)
    ax_c.set_yticks(y)
    ax_c.set_yticklabels([MACRO_LABELS[m] for m in macros], fontsize=9)
    ax_c.set_xlabel("mol ATP", fontsize=9)
    ax_c.set_title("Estimasi ATP (mol)", fontsize=10, pad=6)
    ax_c.grid(axis="x", zorder=0)
    _styled_spine(ax_c, ("bottom", "left"))
    for val, yi in zip(atp_vals, y):
        ax_c.text(val * 0.97, yi, f"{val:.2f}", ha="right", va="center",
                  fontsize=8, color=PALETTE["bg"], fontweight="bold")

    # Panel D: Kotak identitas status gizi RDA harian
    ax_d = fig.add_subplot(gs[1, 0])
    ax_d.set_facecolor(PALETTE["panel"])
    ax_d.axis("off")
    ax_d.set_title("Klasifikasi Diet", fontsize=10, pad=6)

    label = diet.get("label", "—")
    sesuai = diet.get("sesuai_rda", False)
    badge_c = PALETTE["lipid"] if sesuai else PALETTE["esensial"]

    ax_d.text(0.5, 0.72, label, ha="center", va="center", fontsize=22, fontweight="bold", color=badge_c, transform=ax_d.transAxes)
    rda_str = "✓ Sesuai RDA" if sesuai else "✗ Di Luar RDA"
    ax_d.text(0.5, 0.44, rda_str, ha="center", va="center", fontsize=12, color=badge_c, transform=ax_d.transAxes)

    detail_lines = []
    for m in macros:
        info = detail.get(m, {})
        sym = ("↑" if info.get("status") == "tinggi" else ("↓" if info.get("status") == "rendah" else "✓"))
        rng = info.get("rentang_normal", "")
        pct = info.get("rasio", 0) * 100
        detail_lines.append(f"{sym} {MACRO_LABELS[m]}: {pct:.0f}%  [{rng}]")
    ax_d.text(0.5, 0.18, "\n".join(detail_lines), ha="center", va="center", fontsize=8.5, color=PALETTE["subtext"], transform=ax_d.transAxes, linespacing=1.6)

    # Panel E: Grafik 10 kadar asam amino tertinggi
    ax_e = fig.add_subplot(gs[1, 1:])
    ax_e.set_facecolor(PALETTE["panel"])
    aa_bd = export_dict.get("breakdown_asam_amino")

    if aa_bd:
        non_zero = {aa: g for aa, g in aa_bd.items() if g > 0}
        top_items = sorted(non_zero.items(), key=lambda x: x[1], reverse=True)[:10]
        names = [aa.capitalize() for aa, _ in top_items]
        grams = [g for _, g in top_items]
        raw = [aa for aa, _ in top_items]
        colors_aa = [PALETTE["esensial"] if aa in ESSENTIAL_AMINO_ACIDS else PALETTE["non_esensial"] for aa in raw]
        xp = np.arange(len(names))
        ax_e.bar(xp, grams, color=colors_aa, width=0.65, linewidth=0, zorder=3)
        ax_e.set_xticks(xp)
        ax_e.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
        ax_e.set_ylabel("gram", fontsize=9)
        ax_e.set_title("Top 10 Asam Amino (gram) | Merah muda = Esensial", fontsize=10, pad=6)
        ax_e.grid(axis="y", zorder=0)
        _styled_spine(ax_e, ("bottom", "left"))
    else:
        ax_e.axis("off")
        ax_e.text(0.5, 0.5, "Data asam amino tidak tersedia", ha="center", va="center", color=PALETTE["subtext"], fontsize=10, transform=ax_e.transAxes)

    _watermark(fig, "IF3211 Domain-Specific Computation")
    if save_path:
        fig.savefig(save_path)
    return fig


def _bar(value: float, max_val: float, width: int = 24, char: str = "█") -> str:
    """Menggambar bagan bar tekstual untuk terminal."""
    filled = int(round(value / max_val * width)) if max_val else 0
    return char * filled + "░" * (width - filled)


def print_dashboard(export_dict: dict) -> None:
    """Mencetak dashboard ringkasan hasil kalkulasi dalam bentuk UI teks di console CLI."""
    SEP = "═" * 64
    LINE = "─" * 64
    W = 64

    energi = export_dict["energi"]
    rasio = export_dict["rasio_kalori"]
    atp = export_dict["atp"]
    diet = export_dict["klasifikasi_diet"]
    meta = export_dict.get("metadata", {})

    print(f"\n{SEP}")
    print("  PEMODELAN KOMPUTASI EKIVALEN ENERGI MAKROMOLEKUL".center(W))
    print(f"  {meta.get('timestamp','')[:19]} | versi {meta.get('versi','1.0')}".center(W))
    print(SEP)

    print(f"\n  1. ENERGI (Atwater) Total: {energi['total_kcal']:.2f} kkal")
    print(f"  {LINE[:52]}")
    macros_ui = [
        ("Karbohidrat", "karbohidrat_kcal", "karbohidrat_ratio"),
        ("Protein    ", "protein_kcal",     "protein_ratio"),
        ("Lipid      ", "lipid_kcal",       "lipid_ratio"),
    ]
    for label, kk, rk in macros_ui:
        pct = rasio[rk] * 100
        bar = _bar(rasio[rk], 1.0)
        print(f"  {label}  {bar}  {pct:5.1f}%  ({energi[kk]:.1f} kkal)")

    print(f"\n  2. ESTIMASI ATP Total: {atp['total_atp']:.4f} mol")
    print(f"  {LINE[:52]}")
    max_atp = atp["total_atp"] or 1
    atp_ui = [
        ("Karbohidrat", "karbohidrat_atp"),
        ("Protein    ", "protein_atp"),
        ("Lipid      ", "lipid_atp"),
    ]
    for label, ak in atp_ui:
        bar = _bar(atp[ak], max_atp)
        print(f"  {label}  {bar}  {atp[ak]:.4f} mol")

    print(f"\n  3. KLASIFIKASI DIET")
    print(f"  {LINE[:52]}")
    sesuai = diet.get("sesuai_rda", False)
    badge = "✓ Sesuai RDA" if sesuai else "✗ Di Luar RDA"
    print(f"  Label : {diet['label']} | {badge}")
    detail = diet.get("detail", {})
    for macro, info in detail.items():
        sym = "↑" if info["status"] == "tinggi" else ("↓" if info["status"] == "rendah" else "✓")
        pct = info["rasio"] * 100
        rng = info["rentang_normal"]
        print(f"  {sym} {macro.capitalize():<14}  {pct:5.1f}%   normal: {rng}")

    aa_bd = export_dict.get("breakdown_asam_amino")
    if aa_bd:
        non_zero = {aa: g for aa, g in aa_bd.items() if g > 0}
        total_aa = sum(non_zero.values())
        ess_g = sum(g for aa, g in non_zero.items() if aa in ESSENTIAL_AMINO_ACIDS)
        ne_g = total_aa - ess_g
        print(f"\n  4. PROFIL ASAM AMINO")
        print(f"  {LINE[:52]}")
        print(f"  Total AA terhitung : {total_aa:.4f} g")
        print(f"  Esensial           : {ess_g:.4f} g ({ess_g/total_aa*100:.1f}%)")
        print(f"  Non-Esensial       : {ne_g:.4f} g ({ne_g/total_aa*100:.1f}%)")
        top3 = sorted(non_zero.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"  Top-3 AA           : " + " | ".join(f"{aa} {g:.2f}g" for aa, g in top3))

    atp_det = export_dict.get("atp_detail_per_aa")
    if atp_det:
        print(f"\n  5. ATP DETAIL (per AA)")
        print(f"  {LINE[:52]}")
        print(f"  Total (individual) : {atp_det['total_atp']:.4f} mol")
        print(f"  Metode             : {atp_det['metode']}")

    print(f"\n{SEP}\n")


def visualize_all(
    export_dict: dict,
    save_dir: str | Path = "plots",
    protein_source: str = "sumber_protein",
    show_terminal_dashboard: bool = True,
) -> dict[str, Path]:
    """Eksekusi pembuatan dan penyimpanan semua visualisasi data kuantitatif ke direktori luaran."""
    out_dir = Path(save_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if show_terminal_dashboard:
        print_dashboard(export_dict)

    saved: dict[str, Path] = {}

    def _save(name: str, fig: Optional[plt.Figure]) -> None:
        if fig is None:
            return
        p = out_dir / f"{name}.png"
        fig.savefig(p, dpi=DPI, bbox_inches="tight", facecolor=PALETTE["bg"])
        plt.close(fig)
        saved[name] = p
        print(f"  [saved] {p}")

    print("Membuat visualisasi...")

    _save("01_calorie_distribution",
          plot_calorie_distribution(
              export_dict["rasio_kalori"],
              export_dict["energi"],
              export_dict["klasifikasi_diet"],
          ))

    _save("02_atp_comparison",
          plot_atp_comparison(
              export_dict["atp"],
              export_dict["energi"],
          ))

    if "breakdown_asam_amino" in export_dict:
        _save("03_amino_acid_profile",
              plot_amino_acid_profile(
                  export_dict["breakdown_asam_amino"],
                  protein_source=protein_source,
              ))

    if "atp_detail_per_aa" in export_dict:
        _save("04_atp_per_amino_acid",
              plot_atp_per_amino_acid(
                  export_dict["atp_detail_per_aa"],
              ))

    _save("00_dashboard_summary", plot_dashboard_summary(export_dict))

    print(f"\nSelesai - {len(saved)} plot disimpan ke '{out_dir.resolve()}'")
    return saved


DEMO_DATA: dict = {
    "metadata": {
        "timestamp": "2026-05-29T08:47:32",
        "versi": "1.0",
        "sumber": "anggota1 - Backend & Core Algorithm",
    },
    "input": {"karbohidrat_g": 45.0, "protein_g": 60.0, "lipid_g": 20.0},
    "energi": {
        "karbohidrat_kcal": 180.0, "protein_kcal": 240.0,
        "lipid_kcal": 180.0,       "total_kcal": 600.0,
    },
    "rasio_kalori": {
        "karbohidrat_ratio": 0.3, "protein_ratio": 0.4, "lipid_ratio": 0.3,
    },
    "atp": {
        "karbohidrat_atp": 9.4916, "lipid_atp": 10.0616, "protein_atp": 30.0,
        "total_atp": 49.5532,
        "metode": "rata-rata per gram (estimasi kasar)",
    },
    "klasifikasi_diet": {
        "label": "High-Protein", "sesuai_rda": False,
        "detail": {
            "karbohidrat": {"rasio": 0.3, "rentang_normal": "45%–65%", "status": "rendah"},
            "lipid":       {"rasio": 0.3, "rentang_normal": "20%–35%", "status": "normal"},
            "protein":     {"rasio": 0.4, "rentang_normal": "10%–35%", "status": "tinggi"},
        },
    },
    "breakdown_asam_amino": {
        "leusin": 4.542, "lisin": 5.334, "valin": 2.904, "isoleusin": 3.036,
        "fenilalanin": 2.358, "treonin": 2.67, "metionin": 1.626,
        "triptofan": 0.702, "histidin": 1.878, "arginin": 3.834,
        "alanin": 3.564, "aspartat": 5.412, "glutamat": 8.862,
        "glisin": 2.52, "prolin": 2.256, "serin": 2.268,
        "sistein": 0.744, "tirosin": 1.98, "asparagin": 0.0, "glutamin": 0.0,
    },
    "atp_detail_per_aa": {
        "atp_per_asam_amino": {
            "leusin": 1.454326, "lisin": 1.532444, "valin": 0.793239,
            "isoleusin": 0.925821, "fenilalanin": 0.471058, "treonin": 0.381044,
            "metionin": 0.348717, "histidin": 0.326798, "arginin": 0.594248,
            "alanin": 0.680076, "aspartat": 1.097851, "glutamat": 1.626276,
            "glisin": 0.570972, "prolin": 0.529071, "serin": 0.366886,
            "sistein": 0.104391, "tirosin": 0.360616,
        },
        "total_atp": 12.1638,
        "metode": "per asam amino individual (estimasi akurat)",
    },
}


def main() -> None:
    """Fungsi eksekusi CLI utama skrip visualisasi."""
    if len(sys.argv) >= 2:
        json_path = Path(sys.argv[1])
        if not json_path.exists():
            print(f"[ERROR] File tidak ditemukan: {json_path}", file=sys.stderr)
            sys.exit(1)
        export_dict = json.loads(json_path.read_text(encoding="utf-8"))
        src = json_path.stem.replace("output_", "").replace("-", "_")
    else:
        print("Tidak ada argumen JSON - menggunakan data demo otomatis")
        export_dict = DEMO_DATA
        src = "daging_ayam"

    visualize_all(export_dict, save_dir="plots", protein_source=src)


if __name__ == "__main__":
    main()