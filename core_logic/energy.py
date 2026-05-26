# energy.py — Fitur 1: Kalkulator Energi (kkal per makronutrien + total)

from constants import ATWATER_FACTOR


def calculate_energy(karbohidrat_g: float, protein_g: float, lipid_g: float) -> dict:
    """
    Hitung energi (kkal) dari masing-masing makronutrien menggunakan Atwater Factor.

    Args:
        karbohidrat_g: gram karbohidrat
        protein_g:     gram protein
        lipid_g:       gram lipid/lemak

    Returns:
        dict dengan kunci:
            karbohidrat_kcal, protein_kcal, lipid_kcal, total_kcal  (semua float)
    """
    _validate_non_negative(karbohidrat_g, protein_g, lipid_g)

    karbo_kcal   = karbohidrat_g * ATWATER_FACTOR["karbohidrat"]
    protein_kcal = protein_g     * ATWATER_FACTOR["protein"]
    lipid_kcal   = lipid_g       * ATWATER_FACTOR["lipid"]
    total_kcal   = karbo_kcal + protein_kcal + lipid_kcal

    return {
        "karbohidrat_kcal": round(karbo_kcal,   4),
        "protein_kcal":     round(protein_kcal, 4),
        "lipid_kcal":       round(lipid_kcal,   4),
        "total_kcal":       round(total_kcal,   4),
    }


def calculate_calorie_ratio(energy_result: dict) -> dict:
    """
    Hitung rasio kalori setiap makronutrien terhadap total kalori.

    Args:
        energy_result: output dari calculate_energy()

    Returns:
        dict dengan kunci:
            karbohidrat_ratio, protein_ratio, lipid_ratio  (float 0–1)
    """
    total = energy_result["total_kcal"]
    if total == 0:
        return {
            "karbohidrat_ratio": 0.0,
            "protein_ratio":     0.0,
            "lipid_ratio":       0.0,
        }

    return {
        "karbohidrat_ratio": round(energy_result["karbohidrat_kcal"] / total, 4),
        "protein_ratio":     round(energy_result["protein_kcal"]     / total, 4),
        "lipid_ratio":       round(energy_result["lipid_kcal"]       / total, 4),
    }


# ── helper ───────────────────────────────────────────────────────────────────

def _validate_non_negative(*values: float) -> None:
    if any(v < 0 for v in values):
        raise ValueError("Gram makronutrien tidak boleh negatif.")
