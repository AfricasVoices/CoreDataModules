class EthiopiaCodes(object):
    ETHIOPIAN_TELEPHONE = "ethiopian telephone"

    # Regions
    ADDIS_ABABA = "addis ababa"
    AFAR = "afar"
    AMHARA = "amhara"
    BENISHANGUL_GUMZ = "benishangul gumz"
    DIRE_DAWA = "dire dawa"
    GAMBELA = "gambela"
    HARARI = "harari"
    OROMIA = "oromia"
    SIDAMA = "sidama"
    SNNP = "snnp"
    SOMALI = "somali"
    TIGRAY = "tigray"

    # Zones
    AFDER = "afder"
    AGNEWAK = "agnewak"
    ALLE = "alle"
    AMARO = "amaro"
    ARSI = "arsi"
    ASOSA = "asosa"
    AWI = "awi"
    AWSI_ZONE_1 = "awsi/zone 1"
    BALE = "bale"
    BASKETO = "basketo"
    BENCH_SHEKO = "bench sheko"
    BORENA = "borena"
    BUNO_BEDELE = "buno bedele"
    BURJI = "burji"
    CENTRAL = "central"
    CENTRAL_GONDAR = "central gondar"
    DAAWA = "daawa"
    DAWURO = "dawuro"
    DERASHE = "derashe"
    DIRE_DAWA_RURAL = "dire dawa rural"
    DIRE_DAWA_URBAN = "dire dawa urban"
    DOOLO = "doolo"
    EAST_BALE = "east bale"
    EAST_GOJAM = "east gojam"
    EAST_HARARGE = "east hararge"
    EAST_SHEWA = "east shewa"
    EAST_WELLEGA = "east wellega"
    EASTERN = "eastern"
    ERER = "erer"
    FAFAN = "fafan"
    FANTI_ZONE_4 = "fanti/zone 4"
    FINFINE_SPECIAL = "finfine special"
    GABI_ZONE_3 = "gabi/zone 3"
    GAMO = "gamo"
    GEDEO = "gedeo"
    GOFA = "gofa"
    GUJI = "guji"
    GURAGHE = "guraghe"
    HADIYA = "hadiya"
    HALABA_SPECIAL = "halaba special"
    HARARI = "harari"  # (Shadows region name "harari")
    HARI_ZONE_5 = "hari/zone 5"
    HORO_GUDRU_WELLEGA = "horo gudru wellega"
    ILU_ABA_BORA = "ilu aba bora"
    ITANG_SPECIAL_WOREDA = "itang special woreda"
    JARAR = "jarar"
    JIMMA = "jimma"
    KEFA = "kefa"
    KELEM_WELLEGA = "kelem wellega"
    KEMASHI = "kemashi"
    KEMBATA_TIBARO = "kembata tibaro"
    KILBATI_ZONE_2 = "kilbati/zone 2"
    KONSO = "konso"
    KONTA_SPECIAL = "konta special"
    KORAHE = "korahe"
    LIBAN = "liban"
    MAJANG = "majang"
    MAO_KOMO_SPECIAL = "mao komo special"
    MEKELLE = "mekelle"
    METEKEL = "metekel"
    MIRAB_OMO = "mirab omo"
    NOGOB = "nogob"
    NORTH_GONDAR = "north gondar"
    NORTH_SHEWA_AM = "north shewa (am)"
    NORTH_SHEWA_OR = "north shewa (or)"
    NORTH_WELLO = "north wello"
    NORTH_WESTERN = "north western"
    NUWER = "nuwer"
    OROMIA = "oromia"  # (Shadows region name "oromia")
    REGION_14 = "region 14"
    SHABELLE = "shabelle"
    SHEKA = "sheka"
    SIDAMA = "sidama"  # (Shadows region name "sidima")
    SILTIE = "siltie"
    SITI = "siti"
    SOUTH_EASTERN = "south eastern"
    SOUTH_GONDAR = "south gondar"
    SOUTH_OMO = "south omo"
    SOUTH_WELLO = "south wello"
    SOUTH_WEST_SHEWA = "south west shewa"
    SOUTHERN = "southern"
    WAG_HAMRA = "wag hamra"
    WEST_ARSI = "west arsi"
    WEST_GOJAM = "west gojam"
    WEST_GONDAR = "west gondar"
    WEST_GUJI = "west guji"
    WEST_HARARGE = "west hararge"
    WEST_SHEWA = "west shewa"
    WEST_WELLEGA = "west wellega"
    WESTERN = "western"
    WOLAYITA = "wolayita"
    YEM_SPECIAL = "yem special"

    ZONE_TO_REGION_MAP = {
        AFDER: SOMALI,
        AGNEWAK: GAMBELA,
        ALLE: SNNP,
        AMARO: SNNP,
        ARSI: OROMIA,
        ASOSA: BENISHANGUL_GUMZ,
        AWI: AMHARA,
        AWSI_ZONE_1: AFAR,
        BALE: OROMIA,
        BASKETO: SNNP,
        BENCH_SHEKO: SNNP,
        BORENA: OROMIA,
        BUNO_BEDELE: OROMIA,
        BURJI: SNNP,
        CENTRAL: TIGRAY,
        CENTRAL_GONDAR: AMHARA,
        DAAWA: SOMALI,
        DAWURO: SNNP,
        DERASHE: SNNP,
        DIRE_DAWA_RURAL: DIRE_DAWA,
        DIRE_DAWA_URBAN: DIRE_DAWA,
        DOOLO: SOMALI,
        EAST_BALE: OROMIA,
        EAST_GOJAM: AMHARA,
        EAST_HARARGE: OROMIA,
        EAST_SHEWA: OROMIA,
        EAST_WELLEGA: OROMIA,
        EASTERN: TIGRAY,
        ERER: SOMALI,
        FAFAN: SOMALI,
        FANTI_ZONE_4: AFAR,
        FINFINE_SPECIAL: OROMIA,
        GABI_ZONE_3: AFAR,
        GAMO: SNNP,
        GEDEO: SNNP,
        GOFA: SNNP,
        GUJI: OROMIA,
        GURAGHE: SNNP,
        HADIYA: SNNP,
        HALABA_SPECIAL: SNNP,
        HARARI: HARARI,
        HARI_ZONE_5: AFAR,
        HORO_GUDRU_WELLEGA: OROMIA,
        ILU_ABA_BORA: OROMIA,
        ITANG_SPECIAL_WOREDA: GAMBELA,
        JARAR: SOMALI,
        JIMMA: OROMIA,
        KEFA: SNNP,
        KELEM_WELLEGA: OROMIA,
        KEMASHI: BENISHANGUL_GUMZ,
        KEMBATA_TIBARO: SNNP,
        KILBATI_ZONE_2: AFAR,
        KONSO: SNNP,
        KONTA_SPECIAL: SNNP,
        KORAHE: SOMALI,
        LIBAN: SOMALI,
        MAJANG: GAMBELA,
        MAO_KOMO_SPECIAL: BENISHANGUL_GUMZ,
        MEKELLE: TIGRAY,
        METEKEL: BENISHANGUL_GUMZ,
        MIRAB_OMO: SNNP,
        NOGOB: SOMALI,
        NORTH_GONDAR: AMHARA,
        NORTH_SHEWA_AM: AMHARA,
        NORTH_SHEWA_OR: OROMIA,
        NORTH_WELLO: AMHARA,
        NORTH_WESTERN: TIGRAY,
        NUWER: GAMBELA,
        OROMIA: AMHARA,
        REGION_14: ADDIS_ABABA,
        SHABELLE: SOMALI,
        SHEKA: SNNP,
        SIDAMA: SIDAMA,
        SILTIE: SNNP,
        SITI: SOMALI,
        SOUTH_EASTERN: TIGRAY,
        SOUTH_GONDAR: AMHARA,
        SOUTH_OMO: SNNP,
        SOUTH_WELLO: AMHARA,
        SOUTH_WEST_SHEWA: OROMIA,
        SOUTHERN: TIGRAY,
        WAG_HAMRA: AMHARA,
        WEST_ARSI: OROMIA,
        WEST_GOJAM: AMHARA,
        WEST_GONDAR: AMHARA,
        WEST_GUJI: OROMIA,
        WEST_HARARGE: OROMIA,
        WEST_SHEWA: OROMIA,
        WEST_WELLEGA: OROMIA,
        WESTERN: TIGRAY,
        WOLAYITA: SNNP,
        YEM_SPECIAL: SNNP,
    }

    ZONES = list(ZONE_TO_REGION_MAP.keys())

    REGIONS = list(set(ZONE_TO_REGION_MAP.values()))
