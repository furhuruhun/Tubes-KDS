# diet.py — Fitur 3: Klasifikasi Diet berdasarkan rasio kalori (standar IOM)

from constants import DIET_RATIO_STANDARD


def classify_diet(ratio_result: dict) -> dict:
    """
    Klasifikasi diet berdasarkan rasio kalori terhadap rentang normal IOM.

    Label yang mungkin:
        "Balanced"      — semua makronutrien dalam rentang normal
        "High-Carb"     — karbohidrat > 65 %
        "Low-Carb"      — karbohidrat < 45 %  (non-ketogenik)
        "Ketogenic"     — lemak > 60 % DAN karbo < 20 %
        "High-Fat"      — lemak > 35 %  (non-ketogenik)
        "Low-Fat"       — lemak < 20 %
        "High-Protein"  — protein > 35 %
        "Low-Protein"   — protein < 10 %
        "Unclassified"  — kombinasi tidak masuk pola di atas

    Args:
        ratio_result: output dari calculate_calorie_ratio()
                      — dict dengan karbohidrat_ratio, protein_ratio, lipid_ratio

    Returns:
        dict dengan kunci:
            label        (str),
            sesuai_rda   (bool),
            detail       ({makro: {rasio, rentang_normal, status}})
    """
    karbo_r   = ratio_result["karbohidrat_ratio"]
    protein_r = ratio_result["protein_ratio"]
    lipid_r   = ratio_result["lipid_ratio"]

    karbo_min,   karbo_max   = DIET_RATIO_STANDARD["karbohidrat"]
    lipid_min,   lipid_max   = DIET_RATIO_STANDARD["lipid"]
    protein_min, protein_max = DIET_RATIO_STANDARD["protein"]

    karbo_status   = _status(karbo_r,   karbo_min,   karbo_max)
    lipid_status   = _status(lipid_r,   lipid_min,   lipid_max)
    protein_status = _status(protein_r, protein_min, protein_max)

    all_normal = (karbo_status == lipid_status == protein_status == "normal")
    label = _determine_label(
        karbo_r, protein_r, lipid_r,
        karbo_status, protein_status, lipid_status,
    )

    return {
        "label":      label,
        "sesuai_rda": all_normal,
        "detail": {
            "karbohidrat": {
                "rasio":         karbo_r,
                "rentang_normal": f"{karbo_min*100:.0f}%–{karbo_max*100:.0f}%",
                "status":         karbo_status,
            },
            "lipid": {
                "rasio":         lipid_r,
                "rentang_normal": f"{lipid_min*100:.0f}%–{lipid_max*100:.0f}%",
                "status":         lipid_status,
            },
            "protein": {
                "rasio":         protein_r,
                "rentang_normal": f"{protein_min*100:.0f}%–{protein_max*100:.0f}%",
                "status":         protein_status,
            },
        },
    }


# ── helpers ──────────────────────────────────────────────────────────────────

def _status(value: float, min_val: float, max_val: float) -> str:
    if value < min_val:
        return "rendah"
    if value > max_val:
        return "tinggi"
    return "normal"


def _determine_label(
    karbo_r: float, protein_r: float, lipid_r: float,
    karbo_status: str, protein_status: str, lipid_status: str,
) -> str:
    if karbo_status == lipid_status == protein_status == "normal":
        return "Balanced"

    # Ketogenik: lemak sangat dominan dan karbo sangat rendah
    if lipid_r > 0.60 and karbo_r < 0.20:
        return "Ketogenic"

    # Tentukan status yang paling menyimpang (prioritas: tinggi > rendah)
    deviations = []
    if karbo_status   == "tinggi":  deviations.append(("High-Carb",    karbo_r))
    if lipid_status   == "tinggi":  deviations.append(("High-Fat",     lipid_r))
    if protein_status == "tinggi":  deviations.append(("High-Protein", protein_r))

    if deviations:
        # Pilih label dari makronutrien yang rasionya paling tinggi
        return max(deviations, key=lambda x: x[1])[0]

    if karbo_status   == "rendah":  return "Low-Carb"
    if lipid_status   == "rendah":  return "Low-Fat"
    if protein_status == "rendah":  return "Low-Protein"

    return "Unclassified"
