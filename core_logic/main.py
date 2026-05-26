#!/usr/bin/env python3

from energy     import calculate_energy, calculate_calorie_ratio
from atp        import estimate_atp_basic, estimate_atp_from_amino_acids
from diet       import classify_diet
from amino_acid import get_amino_acid_breakdown, get_available_sources
from export     import build_export_dict, save_csv, save_json
from constants  import ESSENTIAL_AMINO_ACIDS

SEP  = "=" * 62
LINE = "─" * 50



def print_header() -> None:
    print(SEP)
    print("   PEMODELAN KOMPUTASI EKIVALEN ENERGI MAKROMOLEKUL")
    print(SEP)


def display_energy(energy: dict, ratio: dict) -> None:
    print(f"\n{LINE}")
    print("[FITUR 1]  KALKULATOR ENERGI")
    print(f"  {'Makronutrien':<14} {'kkal':>10}   {'%':>6}")
    print(f"  {'─'*34}")
    for macro, kcal_key, ratio_key in [
        ("Karbohidrat", "karbohidrat_kcal", "karbohidrat_ratio"),
        ("Protein",     "protein_kcal",     "protein_ratio"),
        ("Lipid",       "lipid_kcal",       "lipid_ratio"),
    ]:
        pct = ratio[ratio_key] * 100
        print(f"  {macro:<14} {energy[kcal_key]:>10.2f}   {pct:>5.1f}%")
    print(f"  {'─'*34}")
    print(f"  {'TOTAL':<14} {energy['total_kcal']:>10.2f}")


def display_atp(atp: dict) -> None:
    print(f"\n{LINE}")
    print("ESTIMASI ATP")
    print(f"  {'Makronutrien':<14} {'mol ATP':>12}")
    print(f"  {'─'*28}")
    for macro, key in [
        ("Karbohidrat", "karbohidrat_atp"),
        ("Lipid",       "lipid_atp"),
        ("Protein",     "protein_atp"),
    ]:
        print(f"  {macro:<14} {atp[key]:>12.4f}")
    print(f"  {'─'*28}")
    print(f"  {'TOTAL':<14} {atp['total_atp']:>12.4f}")
    print(f"  Metode : {atp['metode']}")


def display_diet(diet: dict) -> None:
    status_symbol = {"normal": "✓", "rendah": "↓", "tinggi": "↑"}

    print(f"\n{LINE}")
    print("[FITUR 2]  KLASIFIKASI DIET")
    print(f"  Label      : {diet['label']}")
    print(f"  Sesuai RDA : {'Ya ✓' if diet['sesuai_rda'] else 'Tidak ✗'}")
    print(f"\n  Detail per makronutrien:")
    print(f"  {'Makronutrien':<14} {'Rasio':>7}   {'Rentang Normal':>15}   Status")
    print(f"  {'─'*54}")
    for macro, info in diet["detail"].items():
        pct    = info["rasio"] * 100
        sym    = status_symbol.get(info["status"], "?")
        status = info["status"]
        print(
            f"  {macro.capitalize():<14} {pct:>6.1f}%"
            f"   {info['rentang_normal']:>15}   {sym} {status}"
        )


def display_aa_breakdown(aa_breakdown: dict, protein_source: str) -> None:
    print(f"\n{LINE}")
    print(f"BREAKDOWN ASAM AMINO — {protein_source.upper().replace('_', ' ')}")
    print(f"  {'Asam Amino':<16} {'Gram':>8}   Jenis")
    print(f"  {'─'*44}")
    for aa, gram in sorted(aa_breakdown.items(), key=lambda x: -x[1]):
        if gram == 0:
            continue
        jenis = "esensial" if aa in ESSENTIAL_AMINO_ACIDS else "non-esensial"
        print(f"  {aa:<16} {gram:>8.4f} g   {jenis}")


def display_atp_detail(atp_detail: dict) -> None:
    per_aa = atp_detail["atp_per_asam_amino"]

    print(f"\n{LINE}")
    print("ATP DETAIL PER ASAM AMINO")
    print(f"  {'Asam Amino':<16} {'mol ATP':>12}")
    print(f"  {'─'*30}")
    for aa, val in sorted(per_aa.items(), key=lambda x: -x[1]):
        print(f"  {aa:<16} {val:>12.6f}")
    print(f"  {'─'*30}")
    print(f"  {'TOTAL':<16} {atp_detail['total_atp']:>12.4f}")
    print(f"  Metode : {atp_detail['metode']}")


# ── input helpers ─────────────────────────────────────────────────────────────

def prompt_float(pesan: str, allow_zero: bool = True) -> float:
    while True:
        try:
            val = float(input(pesan))
            if val < 0:
                print("  [!] Nilai tidak boleh negatif.")
                continue
            if not allow_zero and val == 0:
                print("  [!] Nilai harus lebih dari 0.")
                continue
            return val
        except ValueError:
            print("  [!] Input tidak valid — masukkan angka.")


def prompt_makronutrien() -> tuple[float, float, float]:
    print(f"\n[INPUT MAKRONUTRIEN]")
    karbo   = prompt_float("  Karbohidrat (gram) : ")
    protein = prompt_float("  Protein      (gram) : ")
    lipid   = prompt_float("  Lipid/Lemak  (gram) : ")
    return karbo, protein, lipid


def prompt_protein_source() -> tuple[str, float]:
    sources = get_available_sources()
    print(f"\n[INPUT SUMBER PROTEIN]")
    print(f"  Sumber tersedia : {', '.join(sources)}")

    while True:
        src = input("  Pilih sumber    : ").strip().lower()
        if src in sources:
            break
        print(f"  [!] '{src}' tidak dikenal. Pilih dari: {', '.join(sources)}")

    gram = prompt_float(f"  Gram protein dari {src} : ", allow_zero=False)
    return src, gram


# ── alur utama ────────────────────────────────────────────────────────────────

def run_analisis() -> dict:
    karbo_g, protein_g, lipid_g = prompt_makronutrien()

    energy_result = calculate_energy(karbo_g, protein_g, lipid_g)
    ratio_result  = calculate_calorie_ratio(energy_result)
    atp_result    = estimate_atp_basic(karbo_g, protein_g, lipid_g)
    diet_result   = classify_diet(ratio_result)

    print(f"\n{SEP}")
    display_energy(energy_result, ratio_result)
    display_atp(atp_result)
    display_diet(diet_result)

    src, protein_gram = prompt_protein_source()
    aa_breakdown = get_amino_acid_breakdown(src, protein_gram)
    atp_detail   = estimate_atp_from_amino_acids(aa_breakdown)

    display_aa_breakdown(aa_breakdown, src)
    display_atp_detail(atp_detail)

    input_gram = {
        "karbohidrat_g": karbo_g,
        "protein_g":     protein_g,
        "lipid_g":       lipid_g,
    }
    return build_export_dict(
        input_gram, energy_result, ratio_result, atp_result, diet_result,
        aa_breakdown, atp_detail,
    )


def run_export(export: dict) -> None:
    print(f"\n{LINE}")
    print("[FITUR 4]  EKSPOR DATA")
    print("  (1) CSV   (2) JSON   (3) Keduanya   (0) Lewati")

    pilihan = input("  Pilih format : ").strip()
    if pilihan == "0":
        print("  Export dilewati.")
        return

    nama = input("  Nama file (tanpa ekstensi) [default: hasil_analisis]: ").strip()
    if not nama:
        nama = "hasil_analisis"

    if pilihan in ("1", "3"):
        path = save_csv(export, f"{nama}.csv")
        print(f"  Disimpan : {path.resolve()}")
    if pilihan in ("2", "3"):
        path = save_json(export, f"{nama}.json")
        print(f"  Disimpan : {path.resolve()}")


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    print_header()

    export = run_analisis()
    run_export(export)

    print(f"\n{SEP}")
    print("  Analisis selesai.")
    print(SEP)


if __name__ == "__main__":
    main()
