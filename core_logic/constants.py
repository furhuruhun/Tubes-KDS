# constants.py — Data konstanta untuk komputasi energi makromolekul
# Referensi lengkap ada di requirements_anggota1.md

# ── Atwater Factor ──────────────────────────────────────────────────────────
# Merrill & Watt (1973). USDA Agriculture Handbook No. 74.
ATWATER_FACTOR = {
    "karbohidrat": 4.0,   # kkal/gram
    "protein":     4.0,   # kkal/gram
    "lipid":       9.0,   # kkal/gram
}

# ── Yield ATP per Makronutrien ───────────────────────────────────────────────
# Berg et al. (2002). Biochemistry (5th ed.), Chapter 17 & 22.
# Nelson & Cox (2017). Lehninger Principles of Biochemistry (7th ed.).
ATP_YIELD = {
    "karbohidrat": {
        "atp_per_mol":      38,
        "molecular_weight": 180.16,    # g/mol glukosa (C6H12O6)
        "atp_per_gram":     38 / 180.16,
    },
    "lipid": {
        "atp_per_mol":      129,
        "molecular_weight": 256.42,    # g/mol asam palmitat (C16H32O2)
        "atp_per_gram":     129 / 256.42,
    },
    "protein": {
        "atp_per_gram": 0.5,           # estimasi rata-rata semua asam amino
    },
}

# ── Standar RDA (Institute of Medicine, 2005) ────────────────────────────────
# Rentang persentase dari total kalori harian.
DIET_RATIO_STANDARD = {
    "karbohidrat": (0.45, 0.65),
    "lipid":       (0.20, 0.35),
    "protein":     (0.10, 0.35),
}

# ── Berat Molekul Asam Amino ─────────────────────────────────────────────────
# PubChem / NCBI Compound Database. https://pubchem.ncbi.nlm.nih.gov
MOLECULAR_WEIGHT_AA = {   # g/mol
    "glisin":       75.03,
    "alanin":       89.09,
    "valin":        117.15,
    "leusin":       131.17,
    "isoleusin":    131.17,
    "prolin":       115.13,
    "fenilalanin":  165.19,
    "triptofan":    204.23,
    "metionin":     149.21,
    "serin":        105.09,
    "treonin":      119.12,
    "sistein":      121.16,
    "tirosin":      181.19,
    "asparagin":    132.12,
    "glutamin":     146.15,
    "aspartat":     133.10,
    "glutamat":     147.13,
    "lisin":        146.19,
    "arginin":      174.20,
    "histidin":     155.16,
}

# Asam amino esensial — tidak bisa disintesis tubuh, harus dari makanan.
ESSENTIAL_AMINO_ACIDS = frozenset({
    "histidin", "isoleusin", "leusin", "lisin",
    "metionin", "fenilalanin", "treonin", "triptofan", "valin",
})

# ── Yield ATP per Asam Amino Individual ─────────────────────────────────────
# Berg et al. (2002). Biochemistry (5th ed.), Chapter 23.
ATP_PER_AMINO_ACID = {   # mol ATP per mol asam amino
    # Masuk via Piruvat
    "glisin":       17,
    "alanin":       17,
    "serin":        17,
    "sistein":      17,
    "treonin":      17,
    # Masuk via Asetil-KoA
    "leusin":       42,
    "lisin":        42,
    # Masuk via α-Ketoglutarat
    "glutamat":     27,
    "glutamin":     27,
    "prolin":       27,
    "arginin":      27,
    "histidin":     27,
    # Masuk via Suksinil-KoA
    "valin":        32,
    "metionin":     32,
    # Masuk via Suksinil-KoA + Asetil-KoA
    "isoleusin":    40,
    # Masuk via Fumarat
    "fenilalanin":  33,
    "tirosin":      33,
    "aspartat":     27,
    "asparagin":    27,
}

# ── Komposisi Asam Amino per Sumber Protein ──────────────────────────────────
# Fraksi: gram asam amino per gram total protein.
# USDA FoodData Central (2023). https://fdc.nal.usda.gov
PROTEIN_SOURCE_COMPOSITION = {
    "daging_ayam": {           # FDC ID: 171477
        "leusin":      0.0757,
        "lisin":       0.0889,
        "valin":       0.0484,
        "isoleusin":   0.0506,
        "fenilalanin": 0.0393,
        "treonin":     0.0445,
        "metionin":    0.0271,
        "triptofan":   0.0117,
        "histidin":    0.0313,
        "arginin":     0.0639,
        "alanin":      0.0594,
        "aspartat":    0.0902,
        "glutamat":    0.1477,
        "glisin":      0.0420,
        "prolin":      0.0376,
        "serin":       0.0378,
        "sistein":     0.0124,
        "tirosin":     0.0330,
        "asparagin":   0.0000,
        "glutamin":    0.0000,
    },
    "daging_kambing": {        # FDC ID: 172694
        "leusin":      0.0750,
        "lisin":       0.0818,
        "valin":       0.0473,
        "isoleusin":   0.0456,
        "fenilalanin": 0.0378,
        "treonin":     0.0428,
        "metionin":    0.0236,
        "triptofan":   0.0109,
        "histidin":    0.0303,
        "arginin":     0.0660,
        "alanin":      0.0584,
        "aspartat":    0.0870,
        "glutamat":    0.1420,
        "glisin":      0.0580,
        "prolin":      0.0419,
        "serin":       0.0361,
        "sistein":     0.0115,
        "tirosin":     0.0313,
        "asparagin":   0.0000,
        "glutamin":    0.0000,
    },
    "putih_telur": {           # FDC ID: 172183
        "leusin":      0.0877,
        "lisin":       0.0706,
        "valin":       0.0667,
        "isoleusin":   0.0620,
        "fenilalanin": 0.0659,
        "treonin":     0.0462,
        "metionin":    0.0382,
        "triptofan":   0.0162,
        "histidin":    0.0241,
        "arginin":     0.0609,
        "alanin":      0.0641,
        "aspartat":    0.1180,
        "glutamat":    0.1439,
        "glisin":      0.0354,
        "prolin":      0.0385,
        "serin":       0.0742,
        "sistein":     0.0257,
        "tirosin":     0.0407,
        "asparagin":   0.0000,
        "glutamin":    0.0000,
    },
    "tahu": {                  # FDC ID: 172476
        "leusin":      0.0794,
        "lisin":       0.0634,
        "valin":       0.0502,
        "isoleusin":   0.0493,
        "fenilalanin": 0.0539,
        "treonin":     0.0398,
        "metionin":    0.0136,
        "triptofan":   0.0140,
        "histidin":    0.0263,
        "arginin":     0.0767,
        "alanin":      0.0456,
        "aspartat":    0.1190,
        "glutamat":    0.1884,
        "glisin":      0.0453,
        "prolin":      0.0551,
        "serin":       0.0536,
        "sistein":     0.0150,
        "tirosin":     0.0379,
        "asparagin":   0.0000,
        "glutamin":    0.0000,
    },
}
