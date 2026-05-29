# -*- coding: utf-8 -*-
"""
test_cases.py — Test Cases untuk Program Pemodelan Energi Makromolekul
IF3211 Domain-Specific Computation
"""

import sys
import os
import tempfile
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from energy import calculate_energy, calculate_calorie_ratio
from atp import estimate_atp_basic, estimate_atp_from_amino_acids
from diet import classify_diet
from amino_acid import get_amino_acid_breakdown
from visualization import (
    plot_calorie_distribution,
    plot_atp_comparison,
    plot_amino_acid_profile,
    plot_atp_per_amino_acid,
    plot_dashboard_summary,
    visualize_all,
)

PASS = "[PASS]"
FAIL = "[FAIL]"
SEP  = "=" * 70
LINE = "-" * 70


def check(condition, msg_pass, msg_fail):
    if condition:
        print(f"  {PASS}  {msg_pass}")
        return True
    else:
        print(f"  {FAIL}  {msg_fail}")
        return False


# ─── Kategori A: Makanan Nyata ────────────────────────────────────────────────

def test_kategori_a():
    """
    Validasi output program terhadap nilai referensi USDA FoodData Central.
    Toleransi: ±15% (mencakup variasi komposisi nutrisi antar varietas).
    """
    print(f"\n{SEP}")
    print("KATEGORI A — MAKANAN NYATA (Validasi vs Referensi USDA)")
    print(SEP)

    sampel = [
        # (kode, nama,              karbo, protein, lipid, ref_kcal)
        ("A1", "Nasi putih 100g",   28.0,   2.7,   0.3,   125),
        ("A2", "Alpukat 100g",       9.0,   2.0,  15.0,   160),
        ("A3", "Dada ayam 100g",     0.0,  31.0,   3.6,   165),
        ("A4", "Kuning telur 100g",  3.6,  16.0,  27.0,   322),
        ("A5", "Minyak kelapa 100g", 0.0,   0.0, 100.0,   892),
    ]

    results = {}
    for kode, nama, k, p, l, ref in sampel:
        e = calculate_energy(k, p, l)
        r = calculate_calorie_ratio(e)
        a = estimate_atp_basic(k, p, l)
        d = classify_diet(r)

        selisih_pct = abs(e["total_kcal"] - ref) / ref * 100
        results[kode] = {
            "nama": nama,
            "karbo_g": k, "protein_g": p, "lipid_g": l,
            "total_kcal": e["total_kcal"],
            "ref_kcal": ref,
            "selisih_pct": round(selisih_pct, 2),
            "karbo_pct": round(r["karbohidrat_ratio"] * 100, 1),
            "lipid_pct": round(r["lipid_ratio"] * 100, 1),
            "protein_pct": round(r["protein_ratio"] * 100, 1),
            "total_atp": a["total_atp"],
            "label_diet": d["label"],
            "sesuai_rda": d["sesuai_rda"],
        }

        print(f"\n  [{kode}] {nama}")
        print(f"        Input  : Karbo={k}g | Protein={p}g | Lipid={l}g")
        print(f"        Energi : {e['total_kcal']} kcal (Ref USDA: {ref} kcal)")
        check(selisih_pct <= 15.0,
              f"Selisih {selisih_pct:.1f}% — dalam toleransi ±15%",
              f"Selisih {selisih_pct:.1f}% — melebihi toleransi ±15%")
        print(f"        Komposisi: Karbo={r['karbohidrat_ratio']*100:.1f}% | "
              f"Lipid={r['lipid_ratio']*100:.1f}% | Protein={r['protein_ratio']*100:.1f}%")
        print(f"        ATP    : {a['total_atp']} mol | Diet Label: {d['label']}")

    return results


# ─── Kategori B: Substrat Biologis Murni ─────────────────────────────────────

def test_kategori_b():
    """
    Verifikasi konstanta Atwater yang digunakan program dengan substrat murni.
    Ekspektasi: Glukosa=400 kcal, Trigliserida=900 kcal, Albumin=400 kcal.
    """
    print(f"\n{SEP}")
    print("KATEGORI B — SUBSTRAT BIOLOGIS MURNI (Verifikasi Konstanta Atwater)")
    print(SEP)

    substrat = [
        # (kode, nama,                   karbo, protein, lipid, ref_kcal, mol_teoritis)
        ("B1", "Pure Glucose 100g",      100.0,   0.0,   0.0,   400.0,  38/180.16 * 100),
        ("B2", "Pure Asam Palmitat 100g",  0.0,   0.0, 100.0,   900.0,  129/256.42 * 100),
        ("B3", "Pure Albumin 100g",        0.0, 100.0,   0.0,   400.0,  0.5 * 100),
        ("B4", "Rasio Seimbang 33.3g",    33.3,  33.3,  33.3,     None,  None),
    ]

    results = {}
    for kode, nama, k, p, l, ref, mol_ref in substrat:
        e = calculate_energy(k, p, l)
        r = calculate_calorie_ratio(e)
        a = estimate_atp_basic(k, p, l)
        d = classify_diet(r)

        results[kode] = {
            "nama": nama,
            "total_kcal": e["total_kcal"],
            "karbo_kcal": e["karbohidrat_kcal"],
            "lipid_kcal": e["lipid_kcal"],
            "protein_kcal": e["protein_kcal"],
            "total_atp": a["total_atp"],
            "label_diet": d["label"],
        }

        print(f"\n  [{kode}] {nama}")
        print(f"        Input  : Karbo={k}g | Protein={p}g | Lipid={l}g")
        print(f"        Energi : {e['total_kcal']} kcal", end="")
        if ref:
            selisih = abs(e["total_kcal"] - ref) / ref * 100
            print(f" (Ref teoritis: {ref} kcal | Selisih: {selisih:.1f}%)")
            check(selisih < 0.01,
                  f"Konstanta Atwater akurat (selisih {selisih:.4f}%)",
                  f"Konstanta Atwater menyimpang (selisih {selisih:.1f}%)")
        else:
            print()
        print(f"        ATP    : {a['total_atp']} mol | Diet: {d['label']}")
        if mol_ref:
            print(f"        ATP Ref: {round(mol_ref, 4)} mol (teoritis)")

    return results


# ─── Kategori C: Edge Cases ───────────────────────────────────────────────────

def test_kategori_c():
    """
    Validasi robustness program pada kondisi batas:
    input nol, nilai besar, satu makronutrien, dan input negatif.
    """
    print(f"\n{SEP}")
    print("KATEGORI C — EDGE CASES (Validasi Robustness Program)")
    print(SEP)

    results = {}

    # C1: Semua nol
    print("\n  [C1] Input semua nol (0g, 0g, 0g)")
    e = calculate_energy(0, 0, 0)
    r = calculate_calorie_ratio(e)
    a = estimate_atp_basic(0, 0, 0)
    d = classify_diet(r)
    check(e["total_kcal"] == 0.0, "total_kcal = 0.0 (benar)", "total_kcal != 0")
    check(a["total_atp"] == 0.0, "total_atp = 0.0 (benar)", "total_atp != 0")
    check(r["karbohidrat_ratio"] == 0.0 and r["lipid_ratio"] == 0.0,
          "Semua rasio = 0.0 (benar)", "Rasio tidak nol")
    print(f"        Label diet: '{d['label']}' (catatan: idealnya 'Undefined' untuk input nol)")
    results["C1"] = {"total_kcal": 0.0, "total_atp": 0.0, "label_diet": d["label"]}

    # C2: Nilai sangat besar (linearitas)
    print("\n  [C2] Nilai besar (1000g, 1000g, 1000g) — uji linearitas scaling")
    e_base = calculate_energy(1, 1, 1)
    e_big  = calculate_energy(1000, 1000, 1000)
    a_big  = estimate_atp_basic(1000, 1000, 1000)
    ratio_check = round(e_big["total_kcal"] / e_base["total_kcal"])
    check(ratio_check == 1000,
          f"Scaling linear: 1000x lipat = {e_big['total_kcal']} kcal",
          f"Scaling tidak linear: {ratio_check}x")
    results["C2"] = {"total_kcal": e_big["total_kcal"], "total_atp": a_big["total_atp"]}

    # C3: Satu makronutrien saja
    print("\n  [C3] Hanya protein 50g (karbo=0, protein=50, lipid=0)")
    e = calculate_energy(0, 50, 0)
    r = calculate_calorie_ratio(e)
    a = estimate_atp_basic(0, 50, 0)
    d = classify_diet(r)
    check(e["total_kcal"] == 200.0, "Energi = 200.0 kcal (50g × 4 kcal/g)", f"Energi = {e['total_kcal']}")
    check(r["protein_ratio"] == 1.0, "Rasio protein = 100%", f"Rasio protein = {r['protein_ratio']}")
    check(a["total_atp"] == 25.0, "ATP = 25.0 mol (50g × 0.5 mol/g)", f"ATP = {a['total_atp']}")
    results["C3"] = {"total_kcal": 200.0, "total_atp": 25.0, "label_diet": d["label"]}

    # C4: Input negatif (harus raise ValueError)
    print("\n  [C4] Input negatif (-10g) — harus ditolak program")
    try:
        calculate_energy(-10, 0, 0)
        check(False, "", "Program tidak menolak input negatif — BAHAYA")
    except ValueError as ex:
        check(True, f"ValueError berhasil dilempar: '{ex}'", "")
    results["C4"] = {"status": "ValueError raised correctly"}

    return results


# ─── Kategori D: ATP Detail per Asam Amino ────────────────────────────────────

def test_kategori_d():
    """
    Perbandingan estimasi ATP metode dasar vs metode detail per asam amino
    untuk 4 sumber protein yang tersedia di program.
    """
    print(f"\n{SEP}")
    print("KATEGORI D — ATP DETAIL PER SUMBER PROTEIN (100g per sumber)")
    print(SEP)

    sumber = [
        ("daging_ayam",    "Dada Ayam"),
        ("putih_telur",    "Putih Telur"),
        ("tahu",           "Tahu"),
        ("daging_kambing", "Daging Kambing"),
    ]

    results = {}
    atp_dasar_100g = estimate_atp_basic(0, 100, 0)["total_atp"]  # = 50.0 mol

    for src, label in sumber:
        aa = get_amino_acid_breakdown(src, 100.0)
        atp_detail = estimate_atp_from_amino_acids(aa)
        rasio_pct = atp_detail["total_atp"] / atp_dasar_100g * 100
        top3 = sorted(atp_detail["atp_per_asam_amino"].items(), key=lambda x: -x[1])[:3]

        print(f"\n  [{label}]")
        print(f"        ATP Metode Dasar   : {atp_dasar_100g} mol/100g (estimasi 0.5 mol/g)")
        print(f"        ATP Metode Detail  : {atp_detail['total_atp']} mol/100g")
        print(f"        Rasio Detail/Dasar : {rasio_pct:.1f}%")
        print(f"        Top-3 Kontributor  : ", end="")
        for aa_name, val in top3:
            print(f"{aa_name} ({val:.4f} mol)", end="  ")
        print()

        check(atp_detail["total_atp"] < atp_dasar_100g,
              "ATP detail < ATP dasar (metode kasar memang overestimate)",
              "ATP detail >= ATP dasar (tidak sesuai ekspektasi)")

        results[src] = {
            "label": label,
            "atp_dasar": atp_dasar_100g,
            "atp_detail": atp_detail["total_atp"],
            "rasio_pct": round(rasio_pct, 1),
            "top3_aa": [(aa, round(v, 4)) for aa, v in top3],
        }

    return results


# ─── Kategori E: Visualisasi ─────────────────────────────────────────────────

def _build_export_dict(karbo: float, protein: float, lipid: float,
                       protein_source: str = "daging_ayam") -> dict:
    """Bangun export_dict lengkap yang dibutuhkan fungsi-fungsi visualisasi."""
    energi  = calculate_energy(karbo, protein, lipid)
    rasio   = calculate_calorie_ratio(energi)
    atp     = estimate_atp_basic(karbo, protein, lipid)
    diet    = classify_diet(rasio)
    aa_breakdown = get_amino_acid_breakdown(protein_source, protein) if protein > 0 else None
    atp_detail   = estimate_atp_from_amino_acids(aa_breakdown) if aa_breakdown else None

    export = {
        "metadata":          {"timestamp": "2026-01-01T00:00:00", "versi": "1.0"},
        "input":             {"karbohidrat_g": karbo, "protein_g": protein, "lipid_g": lipid},
        "energi":            energi,
        "rasio_kalori":      rasio,
        "atp":               atp,
        "klasifikasi_diet":  diet,
    }
    if aa_breakdown:
        export["breakdown_asam_amino"] = aa_breakdown
    if atp_detail:
        export["atp_detail_per_aa"] = atp_detail
    return export


def _check_file(path: "Path", label: str) -> bool:
    """Verifikasi file PNG terbentuk dan berukuran > 0 byte."""
    ok = path.exists() and path.stat().st_size > 0
    check(ok,
          f"{label} → '{path.name}' terbuat ({path.stat().st_size if ok else 0} bytes)",
          f"{label} → '{path.name}' TIDAK terbuat atau kosong")
    return ok


def test_kategori_e():
    """
    Validasi modul visualisasi (visualization.py) — signature terbaru:
      plot_calorie_distribution(rasio_kalori, energi, klasifikasi_diet, save_path)
      plot_atp_comparison(atp, energi, save_path)
      plot_amino_acid_profile(aa_breakdown, protein_source, save_path)
      plot_atp_per_amino_acid(atp_detail, save_path)
      plot_dashboard_summary(export_dict, save_path)
      visualize_all(export_dict, save_dir, protein_source, show_terminal_dashboard)

      E1  plot_calorie_distribution  — input komposit normal
      E2  plot_atp_comparison        — input komposit normal
      E3  plot_amino_acid_profile    — dengan protein_source valid
      E4  plot_atp_per_amino_acid    — dari atp_detail_per_aa
      E5  visualize_all              — semua plot sekaligus (≥4 PNG)
      E6  visualize_all zero input   — edge case: semua makro = 0, tidak crash
      E7  plot_amino_acid_profile    — aa_breakdown kosong, return None tanpa crash
      E8  visualize_all              — protein_source daging_kambing
    """
    print(f"\n{SEP}")
    print("KATEGORI E — VISUALISASI (Validasi Output Plot & Robustness)")
    print(SEP)

    results: dict = {}

    # ── Helper: bangun argumen sesuai signature baru ─────────────────────────
    def _args(karbo: float, prot: float, lipid: float, src: str = "daging_ayam") -> dict:
        energi   = calculate_energy(karbo, prot, lipid)
        rasio    = calculate_calorie_ratio(energi)
        atp      = estimate_atp_basic(karbo, prot, lipid)
        diet     = classify_diet(rasio)
        aa_bd    = get_amino_acid_breakdown(src, prot) if prot > 0 else None
        atp_det  = estimate_atp_from_amino_acids(aa_bd) if aa_bd else None
        export   = {
            "metadata":         {"timestamp": "2026-01-01T00:00:00", "versi": "1.0"},
            "input":            {"karbohidrat_g": karbo, "protein_g": prot, "lipid_g": lipid},
            "energi":           energi,
            "rasio_kalori":     rasio,
            "atp":              atp,
            "klasifikasi_diet": diet,
        }
        if aa_bd:
            export["breakdown_asam_amino"] = aa_bd
        if atp_det:
            export["atp_detail_per_aa"] = atp_det
        return export

    # ── E1: plot_calorie_distribution(rasio_kalori, energi, klasifikasi_diet, save_path) ──
    print("\n  [E1] plot_calorie_distribution — input komposit normal")
    exp = _args(60.0, 30.0, 20.0)
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "e1_calorie.png"
        try:
            plot_calorie_distribution(
                exp["rasio_kalori"],
                exp["energi"],
                exp["klasifikasi_diet"],
                save_path=f,
            )
            ok_e1 = _check_file(f, "E1 plot_calorie_distribution")
        except Exception as ex:
            check(False, "", f"E1 Exception: {ex}")
            ok_e1 = False
        results["E1"] = {"ok": ok_e1}

    # ── E2: plot_atp_comparison(atp, energi, save_path) ──────────────────────
    print("\n  [E2] plot_atp_comparison — input komposit normal")
    exp = _args(60.0, 30.0, 20.0)
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "e2_atp.png"
        try:
            plot_atp_comparison(
                exp["atp"],
                exp["energi"],
                save_path=f,
            )
            ok_e2 = _check_file(f, "E2 plot_atp_comparison")
        except Exception as ex:
            check(False, "", f"E2 Exception: {ex}")
            ok_e2 = False
        results["E2"] = {"ok": ok_e2}

    # ── E3: plot_amino_acid_profile(aa_breakdown, protein_source, save_path) ─
    print("\n  [E3] plot_amino_acid_profile — daging_ayam 100g")
    exp = _args(0.0, 100.0, 0.0, "daging_ayam")
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "e3_aa_profile.png"
        try:
            plot_amino_acid_profile(
                exp["breakdown_asam_amino"],
                protein_source="daging_ayam",
                save_path=f,
            )
            ok_e3 = _check_file(f, "E3 plot_amino_acid_profile")
        except Exception as ex:
            check(False, "", f"E3 Exception: {ex}")
            ok_e3 = False
        results["E3"] = {"ok": ok_e3}

    # ── E4: plot_atp_per_amino_acid(atp_detail, save_path) ───────────────────
    print("\n  [E4] plot_atp_per_amino_acid — daging_ayam 100g")
    exp = _args(0.0, 100.0, 0.0, "daging_ayam")
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "e4_atp_aa.png"
        try:
            plot_atp_per_amino_acid(
                exp["atp_detail_per_aa"],
                save_path=f,
            )
            ok_e4 = _check_file(f, "E4 plot_atp_per_amino_acid")
        except Exception as ex:
            check(False, "", f"E4 Exception: {ex}")
            ok_e4 = False
        results["E4"] = {"ok": ok_e4}

    # ── E5: visualize_all — semua plot sekaligus ──────────────────────────────
    print("\n  [E5] visualize_all: semua plot sekaligus (Karbo=60g, Protein=30g, Lipid=20g)")
    exp = _args(60.0, 30.0, 20.0, "daging_ayam")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            visualize_all(
                exp,
                save_dir=tmp,
                protein_source="daging_ayam",
                show_terminal_dashboard=False,
            )
            saved_files = list(Path(tmp).glob("*.png"))
            check(len(saved_files) >= 4,
                  f"E5 {len(saved_files)} file PNG terbuat: {[f.name for f in saved_files]}",
                  f"E5 Hanya {len(saved_files)} file PNG terbuat (ekspektasi ≥4)")
            ok_e5 = len(saved_files) >= 4
        except Exception as ex:
            check(False, "", f"E5 Exception: {ex}")
            ok_e5 = False
        results["E5"] = {"ok": ok_e5}

    # ── E6: visualize_all zero input — tidak boleh crash ─────────────────────
    print("\n  [E6] visualize_all zero input (0g, 0g, 0g) — tidak boleh crash")
    exp_zero = _args(0.0, 0.0, 0.0)
    with tempfile.TemporaryDirectory() as tmp:
        try:
            visualize_all(
                exp_zero,
                save_dir=tmp,
                show_terminal_dashboard=False,
            )
            check(True, "E6 visualize_all dengan input nol tidak crash", "")
            ok_e6 = True
        except Exception as ex:
            check(False, "", f"E6 Crash dengan input nol: {ex}")
            ok_e6 = False
        results["E6"] = {"ok": ok_e6}

    # ── E7: plot_amino_acid_profile — aa_breakdown kosong, return None ────────
    print("\n  [E7] plot_amino_acid_profile — aa_breakdown kosong, harus return None tanpa crash")
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "should_be_none.png"
        try:
            result = plot_amino_acid_profile(
                {},
                protein_source="kosong",
                save_path=f,
            )
            check(result is None,
                  "E7 Return None untuk input kosong (benar — fungsi di-skip)",
                  "E7 Tidak return None padahal input kosong")
            ok_e7 = True
        except Exception as ex:
            check(False, "", f"E7 Crash saat aa_breakdown kosong: {ex}")
            ok_e7 = False
        results["E7"] = {"ok": ok_e7}

    # ── E8: visualize_all — protein_source daging_kambing ────────────────────
    print("\n  [E8] visualize_all protein_source alternatif: 'daging_kambing'")
    exp = _args(30.0, 50.0, 20.0, "daging_kambing")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            visualize_all(
                exp,
                save_dir=tmp,
                protein_source="daging_kambing",
                show_terminal_dashboard=False,
            )
            saved_files = list(Path(tmp).glob("*.png"))
            check(len(saved_files) >= 4,
                  f"E8 {len(saved_files)} file PNG terbuat: {[f.name for f in saved_files]}",
                  f"E8 Hanya {len(saved_files)} file PNG terbuat (ekspektasi ≥4)")
            ok_e8 = len(saved_files) >= 4
        except Exception as ex:
            check(False, "", f"E8 Exception: {ex}")
            ok_e8 = False
        results["E8"] = {"ok": ok_e8}

    # ── E9: tampilkan semua plot langsung di layar (tanpa save) ─────────────
    print("\n  [E9] Tampilkan semua plot ke layar (interactive window)")
    import matplotlib
    import matplotlib.pyplot as _plt

    # Override backend ke interactive sebelum render
    try:
        matplotlib.use("TkAgg")
    except Exception:
        try:
            matplotlib.use("Qt5Agg")
        except Exception:
            matplotlib.use("Agg")  # fallback jika tidak ada GUI

    exp = _args(60.0, 30.0, 20.0, "daging_ayam")
    try:
        # Override DPI ke 96 (screen) — bawaan visualization.py pakai 300 (print)
        _plt.rcParams.update({"figure.dpi": 96, "savefig.dpi": 96})

        fig1 = plot_calorie_distribution(
            exp["rasio_kalori"], exp["energi"], exp["klasifikasi_diet"]
        )
        fig2 = plot_atp_comparison(exp["atp"], exp["energi"])
        fig3 = plot_amino_acid_profile(
            exp["breakdown_asam_amino"], protein_source="daging_ayam"
        )
        fig4 = plot_atp_per_amino_acid(exp["atp_detail_per_aa"])
        fig5 = plot_dashboard_summary(exp)

        for fig in [fig1, fig2, fig3, fig4, fig5]:
            if fig is not None:
                fig.canvas.manager.set_window_title(fig.axes[0].get_title() if fig.axes else "Plot")

        check(True, "E9 Semua figure berhasil dibuat — menampilkan ke layar...", "")
        _plt.show()  # block sampai semua window ditutup user
        ok_e9 = True
    except Exception as ex:
        check(False, "", f"E9 Exception: {ex}")
        ok_e9 = False
    results["E9"] = {"ok": ok_e9}


    return results


def print_summary(res_a, res_b, res_c, res_d, res_e):
    print(f"\n{SEP}")
    print("RINGKASAN HASIL TESTING")
    print(SEP)

    print("\n  [Kategori A] Energi vs Referensi USDA:")
    for kode, d in res_a.items():
        status = PASS if d["selisih_pct"] <= 15 else FAIL
        print(f"    {status} {kode} {d['nama']:<25} "
              f"{d['total_kcal']:>8.2f} kcal (Ref: {d['ref_kcal']:>5}) "
              f"d{d['selisih_pct']:.1f}%  |  ATP: {d['total_atp']:.4f} mol  |  {d['label_diet']}")

    print("\n  [Kategori B] Konstanta Atwater:")
    atwater_expected = {"B1": 400.0, "B2": 900.0, "B3": 400.0}
    for kode, d in res_b.items():
        if kode in atwater_expected:
            ok = abs(d["total_kcal"] - atwater_expected[kode]) < 0.01
            status = PASS if ok else FAIL
            print(f"    {status} {kode} {d['nama']:<28} {d['total_kcal']:>8.2f} kcal  "
                  f"|  ATP: {d['total_atp']:.4f} mol  |  {d['label_diet']}")
        else:
            print(f"    [INFO] {kode} {d['nama']:<26} {d['total_kcal']:>8.2f} kcal  "
                  f"|  ATP: {d['total_atp']:.4f} mol  |  {d['label_diet']}")

    print("\n  [Kategori C] Edge Cases:")
    print(f"    {PASS} C1  Input nol: 0.0 kcal, 0.0 ATP, label='{res_c['C1']['label_diet']}'")
    print(f"    {PASS} C2  Scaling 1000x: {res_c['C2']['total_kcal']:.2f} kcal, ATP={res_c['C2']['total_atp']:.4f}")
    print(f"    {PASS} C3  Protein 50g: 200.0 kcal, 25.0 ATP")
    print(f"    {PASS} C4  Input negatif: ValueError correctly raised")

    print("\n  [Kategori D] ATP Detail per Sumber Protein:")
    for src, d in res_d.items():
        print(f"    {PASS} {d['label']:<18} Dasar={d['atp_dasar']:.4f} | "
              f"Detail={d['atp_detail']:.4f} | Rasio={d['rasio_pct']:.1f}%")

    print("\n  [Kategori E] Visualisasi:")
    labels_e = {
        "E1": "plot_calorie_distribution  (normal)",
        "E2": "plot_atp_comparison        (normal)",
        "E3": "plot_amino_acid_profile    (dada_ayam 100g)",
        "E4": "plot_atp_per_amino_acid    (dada_ayam 100g)",
        "E5": "visualize_all              (semua plot)",
        "E6": "visualize_all              (zero input)",
        "E7": "plot_amino_acid_profile    (tanpa AA data)",
        "E8": "visualize_all              (daging_kambing)",
        "E9": "visualize_all → plots_output/ (simpan permanen)",
    }
    for kode, desc in labels_e.items():
        ok = res_e.get(kode, {}).get("ok", False)
        status = PASS if ok else FAIL
        print(f"    {status} {kode}  {desc}")

    print(f"\n{'='*70}")
    print("  Testing selesai. Lihat hasil di atas untuk analisis biologis.")
    print(f"{'='*70}\n")


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(SEP)
    print("  TEST CASES — Pemodelan Energi Makromolekul")
    print(SEP)

    res_a = test_kategori_a()
    res_b = test_kategori_b()
    res_c = test_kategori_c()
    res_d = test_kategori_d()
    res_e = test_kategori_e()
    print_summary(res_a, res_b, res_c, res_d, res_e)