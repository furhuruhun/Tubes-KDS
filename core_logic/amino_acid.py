# amino_acid.py — Fitur 5: Breakdown Asam Amino per sumber protein

from constants import PROTEIN_SOURCE_COMPOSITION, ESSENTIAL_AMINO_ACIDS

AVAILABLE_SOURCES: list[str] = list(PROTEIN_SOURCE_COMPOSITION.keys())


def get_amino_acid_breakdown(protein_source: str, protein_gram: float) -> dict:
    """
    Hitung gram tiap asam amino dari sumber protein dan jumlah gramnya.

    Rumus:
        gram_aa = protein_gram × fraksi_aa_dalam_sumber

    Args:
        protein_source: nama sumber protein (lihat AVAILABLE_SOURCES)
        protein_gram:   gram protein total

    Returns:
        dict  {nama_aa: gram}  untuk semua 20 asam amino dalam sumber tersebut
    """
    if protein_source not in PROTEIN_SOURCE_COMPOSITION:
        valid = ", ".join(AVAILABLE_SOURCES)
        raise ValueError(
            f"Sumber protein '{protein_source}' tidak tersedia.\n"
            f"Pilihan yang valid: {valid}"
        )
    if protein_gram < 0:
        raise ValueError("Gram protein tidak boleh negatif.")

    composition = PROTEIN_SOURCE_COMPOSITION[protein_source]
    return {aa: round(protein_gram * frac, 4) for aa, frac in composition.items()}


def get_available_sources() -> list[str]:
    """Kembalikan daftar sumber protein yang tersedia."""
    return AVAILABLE_SOURCES.copy()


def split_essential_nonessential(aa_breakdown: dict) -> dict:
    """
    Pisahkan breakdown AA menjadi dua kelompok: esensial dan non-esensial.

    Args:
        aa_breakdown: output dari get_amino_acid_breakdown()

    Returns:
        dict dengan kunci:
            esensial      ({nama_aa: gram})
            non_esensial  ({nama_aa: gram})
    """
    esensial     = {}
    non_esensial = {}

    for aa, gram in aa_breakdown.items():
        if aa in ESSENTIAL_AMINO_ACIDS:
            esensial[aa] = gram
        else:
            non_esensial[aa] = gram

    return {"esensial": esensial, "non_esensial": non_esensial}
