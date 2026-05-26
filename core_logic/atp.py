# atp.py — Fitur 2: Estimasi ATP dasar  |  Fitur 7: ATP detail per asam amino

from constants import ATP_YIELD, ATP_PER_AMINO_ACID, MOLECULAR_WEIGHT_AA


# ── Fitur 2 ──────────────────────────────────────────────────────────────────

def estimate_atp_basic(karbohidrat_g: float, protein_g: float, lipid_g: float) -> dict:
    """
    Estimasi mol ATP dari makronutrien menggunakan yield rata-rata per gram.

    Model:
      • Karbohidrat → glukosa (38 ATP/mol, MW = 180.16 g/mol) → ~0.211 mol ATP/g
      • Lipid       → asam palmitat (129 ATP/mol, MW = 256.42 g/mol) → ~0.503 mol ATP/g
      • Protein     → rata-rata semua AA → 0.5 mol ATP/g (estimasi)

    Args:
        karbohidrat_g: gram karbohidrat
        protein_g:     gram protein
        lipid_g:       gram lipid/lemak

    Returns:
        dict dengan kunci:
            karbohidrat_atp, lipid_atp, protein_atp, total_atp  (mol),
            metode  (str)
    """
    if any(v < 0 for v in [karbohidrat_g, protein_g, lipid_g]):
        raise ValueError("Gram makronutrien tidak boleh negatif.")

    karbo_atp   = karbohidrat_g * ATP_YIELD["karbohidrat"]["atp_per_gram"]
    lipid_atp   = lipid_g       * ATP_YIELD["lipid"]["atp_per_gram"]
    protein_atp = protein_g     * ATP_YIELD["protein"]["atp_per_gram"]
    total_atp   = karbo_atp + lipid_atp + protein_atp

    return {
        "karbohidrat_atp": round(karbo_atp,   4),
        "lipid_atp":       round(lipid_atp,   4),
        "protein_atp":     round(protein_atp, 4),
        "total_atp":       round(total_atp,   4),
        "metode":          "rata-rata per gram (estimasi kasar)",
    }


# ── Fitur 7 ──────────────────────────────────────────────────────────────────

def estimate_atp_from_amino_acids(aa_breakdown: dict) -> dict:
    """
    Estimasi mol ATP lebih akurat dari breakdown asam amino per sumber protein.

    Rumus per AA:
        mol_aa  = gram_aa / MW_aa
        atp_aa  = mol_aa × ATP_PER_AMINO_ACID[aa]

    Args:
        aa_breakdown: output dari get_amino_acid_breakdown() — {nama_aa: gram}

    Returns:
        dict dengan kunci:
            atp_per_asam_amino  ({nama_aa: mol_atp}),
            total_atp           (mol),
            metode              (str)
    """
    atp_per_aa = {}
    total_atp  = 0.0

    for aa_name, aa_gram in aa_breakdown.items():
        if aa_gram <= 0:
            continue

        mw      = MOLECULAR_WEIGHT_AA.get(aa_name)
        atp_mol = ATP_PER_AMINO_ACID.get(aa_name)

        if mw is None or atp_mol is None:
            # Asam amino tidak ada datanya — lewati tanpa crash
            continue

        contribution       = (aa_gram / mw) * atp_mol
        atp_per_aa[aa_name] = round(contribution, 6)
        total_atp          += contribution

    return {
        "atp_per_asam_amino": atp_per_aa,
        "total_atp":          round(total_atp, 4),
        "metode":             "per asam amino individual (estimasi akurat)",
    }
