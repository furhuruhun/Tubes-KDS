# export.py — Fitur 4: Ekspor data ke dict / CSV / JSON untuk Anggota 2

import csv
import io
import json
from datetime import datetime
from pathlib import Path


# ── Builder ───────────────────────────────────────────────────────────────────

def build_export_dict(
    input_gram:        dict,
    energy_result:     dict,
    ratio_result:      dict,
    atp_result:        dict,
    diet_result:       dict,
    aa_breakdown:      dict | None = None,
    atp_detail_result: dict | None = None,
) -> dict:
    """
    Gabungkan seluruh hasil kalkulasi ke dalam satu dict terstruktur.

    Kunci opsional (aa_breakdown, atp_detail_result) hanya disertakan
    jika nilainya bukan None — sehingga Anggota 2 bisa mengecek keberadaannya
    dengan  "breakdown_asam_amino" in data.

    Returns:
        dict yang siap di-serialize ke JSON atau diubah ke CSV.
    """
    export = {
        "metadata": {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "versi":     "1.0",
            "sumber":    "anggota1 — Backend & Core Algorithm",
        },
        "input":            input_gram,
        "energi":           energy_result,
        "rasio_kalori":     ratio_result,
        "atp":              atp_result,
        "klasifikasi_diet": diet_result,
    }

    if aa_breakdown is not None:
        export["breakdown_asam_amino"] = aa_breakdown

    if atp_detail_result is not None:
        export["atp_detail_per_aa"] = atp_detail_result

    return export


# ── CSV ───────────────────────────────────────────────────────────────────────

def export_to_csv_string(export_dict: dict) -> str:
    """
    Konversi hasil kalkulasi ke string CSV.

    Format: seksi berjudul (=== SEKSI ===) untuk mempermudah parsing
    sekaligus keterbacaan manusia.
    """
    buf = io.StringIO()
    w   = csv.writer(buf)

    def section(title: str):
        w.writerow([])
        w.writerow([f"=== {title} ==="])

    # Metadata
    section("METADATA")
    for k, v in export_dict.get("metadata", {}).items():
        w.writerow([k, v])

    # Input
    section("INPUT (gram)")
    w.writerow(["makronutrien", "gram"])
    for k, v in export_dict.get("input", {}).items():
        w.writerow([k, v])

    # Energi
    section("ENERGI (kkal)")
    w.writerow(["makronutrien", "kkal"])
    for k, v in export_dict.get("energi", {}).items():
        w.writerow([k, v])

    # Rasio kalori
    section("RASIO KALORI")
    w.writerow(["makronutrien", "rasio", "persen"])
    for k, v in export_dict.get("rasio_kalori", {}).items():
        w.writerow([k, v, f"{v * 100:.2f}%"])

    # ATP dasar
    section("ESTIMASI ATP DASAR (mol)")
    for k, v in export_dict.get("atp", {}).items():
        w.writerow([k, v])

    # Klasifikasi diet
    section("KLASIFIKASI DIET")
    diet = export_dict.get("klasifikasi_diet", {})
    w.writerow(["label",      diet.get("label",      "-")])
    w.writerow(["sesuai_rda", diet.get("sesuai_rda", "-")])
    w.writerow(["makronutrien", "rasio", "rentang_normal", "status"])
    for macro, info in diet.get("detail", {}).items():
        w.writerow([macro, info["rasio"], info["rentang_normal"], info["status"]])

    # Breakdown asam amino (opsional)
    aa = export_dict.get("breakdown_asam_amino")
    if aa:
        section("BREAKDOWN ASAM AMINO (gram)")
        w.writerow(["asam_amino", "gram"])
        for name, gram in sorted(aa.items(), key=lambda x: -x[1]):
            w.writerow([name, gram])

    # ATP detail per AA (opsional)
    atp_detail = export_dict.get("atp_detail_per_aa")
    if atp_detail:
        section("ATP DETAIL PER ASAM AMINO (mol)")
        w.writerow(["asam_amino", "mol_atp"])
        per_aa = atp_detail.get("atp_per_asam_amino", {})
        for name, val in sorted(per_aa.items(), key=lambda x: -x[1]):
            w.writerow([name, val])
        w.writerow(["TOTAL", atp_detail.get("total_atp", "-")])
        w.writerow(["metode", atp_detail.get("metode", "-")])

    return buf.getvalue()


def save_csv(export_dict: dict, filepath: str | Path) -> Path:
    """Tulis hasil ke file CSV. Kembalikan Path file yang disimpan."""
    path    = Path(filepath)
    content = export_to_csv_string(export_dict)
    path.write_text(content, encoding="utf-8")
    return path


# ── JSON ──────────────────────────────────────────────────────────────────────

def save_json(export_dict: dict, filepath: str | Path) -> Path:
    """Tulis hasil ke file JSON. Kembalikan Path file yang disimpan."""
    path = Path(filepath)
    path.write_text(
        json.dumps(export_dict, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path
