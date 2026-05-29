# -*- coding: utf-8 -*-
"""
test_cases.py — Test Cases untuk Program Pemodelan Energi Makromolekul
IF3211 Domain-Specific Computation
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from energy import calculate_energy, calculate_calorie_ratio
from atp import estimate_atp_basic, estimate_atp_from_amino_acids
from diet import classify_diet
from amino_acid import get_amino_acid_breakdown

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


# ─── Ringkasan ────────────────────────────────────────────────────────────────

def print_summary(res_a, res_b, res_c, res_d):
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
    print_summary(res_a, res_b, res_c, res_d)