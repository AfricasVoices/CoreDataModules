class SomaliaCodes(object):
    # Districts
    ADAN_YABAAL = "adan yabaal"
    AFGOOYE = "afgooye"
    AFMADOW = "afmadow"
    BAARDHEERE = "baardheere"
    BADHAADHE = "badhaadhe"
    BAIDOA = "baidoa"
    BAKI = "baki"
    BALCAD = "balcad"
    BANDARBAYLA = "bandarbayla"
    BARAAWE = "baraawe"
    BELET_WEYNE = "belet weyne"
    BELET_XAAWO = "belet xaawo"
    BERBERA = "berbera"
    BOONDHEERE = "boondheere"
    BORAMA = "borama"
    BOSSASO = "bossaso"
    BUAALE = "bu'aale"
    BULO_BURTO = "bulo burto"
    BURCO = "burco"
    BURTINLE = "burtinle"
    BUUHOODLE = "buuhoodle"
    BUUR_HAKABA = "buur hakaba"
    CABDLCASIIS = "cabdlcasiis"
    CABUDWAAQ = "cabudwaaq"
    CADAADO = "cadaado"
    CADALE = "cadale"
    CALUULA = "caluula"
    CAYNABO = "caynabo"
    CEEL_AFWEYN = "ceel afweyn"
    CEEL_BARDE = "ceel barde"
    CEEL_BUUR = "ceel buur"
    CEEL_DHEER = "ceel dheer"
    CEEL_WAAQ = "ceel waaq"
    CEERIGAABO = "ceerigaabo"
    DAYNILE = "daynile"
    DHARKENLEY = "dharkenley"
    DHUUSAMARREEB = "dhuusamarreeb"
    DIINSOOR = "diinsoor"
    DOOLOW = "doolow"
    EYL = "eyl"
    GAALKACYO = "gaalkacyo"
    GALDOGOB = "galdogob"
    GARBAHAAREY = "garbahaarey"
    GAROWE = "garowe"
    GEBILEY = "gebiley"
    HARGEYSA = "hargeysa"
    HAWL_WADAAG = "hawl wadaag"
    HELIWA = "heliwa"
    HOBYO = "hobyo"
    HODAN = "hodan"
    ISKUSHUBAN = "iskushuban"
    JALALAQSI = "jalalaqsi"
    JAMAAME = "jamaame"
    JARIIBAN = "jariiban"
    JOWHAR = "jowhar"
    JILIB = "jilib"
    KARAAN = "karaan"
    KISMAYO = "kismayo"
    KURTUNWAAREY = "kurtunwaarey"
    LAAS_CAANOOD = "laas caanood"
    LAASQOORAY = "laasqooray"
    LUGHAYE = "lughaye"
    LUUQ = "luuq"
    MARKA = "marka"
    OWDWEYNE = "owdweyne"
    QANDALA = "qandala"
    QANSAX_DHEERE = "qansax dheere"
    QARDHO = "qardho"
    QORYOOLEY = "qoryooley"
    RAB_DHUURE = "rab dhuure"
    SAAKOW = "saakow"
    SABLAALE = "sablaale"
    SHANGAANI = "shangaani"
    SHEIKH = "sheikh"
    SHIBIS = "shibis"
    TALEEX = "taleex"
    TAYEEGLOW = "tayeeglow"
    WAABERI = "waaberi"
    WAAJID = "waajid"
    WADAJIR = "wadajir"
    WARDHIIGLEEY = "wardhiigleey"
    WANLA_WEYN = "wanla weyn"
    XAMAR_JAABJAB = "xamar jaabjab"
    XAMAR_WEYNE = "xamar weyne"
    XARARDHEERE = "xarardheere"
    XUDUN = "xudun"
    XUDUR = "xudur"
    YAAQSHID = "yaaqshid"
    ZEYLAC = "zeylac"
    MOGADISHU = "mogadishu"

    # Alternative district names
    BADHAN = "badhan"
    BULO_MARER = "bulo marer"
    GURICEEL = "guriceel"
    MAHADY = "mahady"
    MATABAAN = "matabaan"
    WARSHEIKH = "warsheikh"

    # Regions
    AWDAL = "awdal"
    BAKOOL = "bakool"
    BANADIR = "banadir"
    BARI = "bari"
    BAY = "bay"
    GALGADUUD = "galgaduud"
    GEDO = "gedo"
    HIRAAN = "hiraan"
    LOWER_JUBA = "lower juba"
    LOWER_SHABELLE = "lower shabelle"
    MIDDLE_JUBA = "middle juba"
    MIDDLE_SHABELLE = "middle shabelle"
    MUDUG = "mudug"
    NUGAAL = "nugaal"
    SANAAG = "sanaag"
    SOOL = "sool"
    TOGDHEER = "togdheer"
    WOQOOYI_GALBEED = "woqooyi galbeed"

    # States
    # BANADIR, as defined above
    GALMUDUG = "galmudug"
    HIR_SHABELLE = "hir-shabelle"
    JUBBALAND = "jubbaland"
    PUNTLAND = "puntland"
    SOMALILAND = "somaliland"
    SOUTH_WEST_STATE = "south west state"

    # Zones
    NEZ = "nez"
    NWZ = "nwz"
    SCZ = "scz"

    # Mobile phone network operators
    GOLIS = "golis"
    HORMUD = "hormud"
    NATIONLINK = "nationlink"
    SOMTEL = "somtel"
    TELESOM = "telesom"

    # Map alternative district names to their canonical names
    CANONICAL_DISTRICT_MAP = {
        BADHAN: JARIIBAN,
        BULO_MARER: MARKA,
        GURICEEL: DHUUSAMARREEB,
        MAHADY: JOWHAR,
        MATABAAN: BELET_WEYNE,
        WARSHEIKH: BALCAD
    }

    MOGADISHU_SUB_DISTRICTS = [
        MOGADISHU,
        BOONDHEERE,
        CABDLCASIIS,
        DAYNILE,
        DHARKENLEY,
        HELIWA,
        HODAN,
        HAWL_WADAAG,
        KARAAN,
        SHANGAANI,
        SHIBIS,
        WAABERI,
        WADAJIR,
        WARDHIIGLEEY,
        XAMAR_JAABJAB,
        XAMAR_WEYNE,
        YAAQSHID
    ]

    DISTRICT_TO_REGION_MAP = {
        ADAN_YABAAL: MIDDLE_SHABELLE,
        AFGOOYE: LOWER_SHABELLE,
        AFMADOW: LOWER_JUBA,
        BAARDHEERE: GEDO,
        BADHAADHE: LOWER_JUBA,
        BAIDOA: BAY,
        BAKI: AWDAL,
        BALCAD: MIDDLE_SHABELLE,
        BANDARBAYLA: BARI,
        BARAAWE: LOWER_SHABELLE,
        BELET_WEYNE: HIRAAN,
        BELET_XAAWO: GEDO,
        BERBERA: WOQOOYI_GALBEED,
        BORAMA: AWDAL,
        BOSSASO: BARI,
        BUAALE: MIDDLE_JUBA,
        BULO_BURTO: HIRAAN,
        BURCO: TOGDHEER,
        BURTINLE: NUGAAL,
        BUUHOODLE: TOGDHEER,
        BUUR_HAKABA: BAY,
        CABUDWAAQ: GALGADUUD,
        CADAADO: GALGADUUD,
        CADALE: MIDDLE_SHABELLE,
        CALUULA: BARI,
        CAYNABO: SOOL,
        CEEL_AFWEYN: SANAAG,
        CEEL_BARDE: BAKOOL,
        CEEL_BUUR: GALGADUUD,
        CEEL_DHEER: GALGADUUD,
        CEEL_WAAQ: GEDO,
        CEERIGAABO: SANAAG,
        DHUUSAMARREEB: GALGADUUD,
        DIINSOOR: BAY,
        DOOLOW: GEDO,
        EYL: NUGAAL,
        GAALKACYO: MUDUG,
        GALDOGOB: MUDUG,
        GARBAHAAREY: GEDO,
        GAROWE: NUGAAL,
        GEBILEY: WOQOOYI_GALBEED,
        HARGEYSA: WOQOOYI_GALBEED,
        HOBYO: MUDUG,
        ISKUSHUBAN: BARI,
        JALALAQSI: HIRAAN,
        JAMAAME: LOWER_JUBA,
        JARIIBAN: MUDUG,
        JILIB: MIDDLE_JUBA,
        JOWHAR: MIDDLE_SHABELLE,
        KISMAYO: LOWER_JUBA,
        KURTUNWAAREY: LOWER_SHABELLE,
        LAAS_CAANOOD: SOOL,
        LAASQOORAY: SANAAG,
        LUGHAYE: AWDAL,
        LUUQ: GEDO,
        MARKA: LOWER_SHABELLE,
        MOGADISHU: BANADIR,
        OWDWEYNE: TOGDHEER,
        QANDALA: BARI,
        QANSAX_DHEERE: BAY,
        QARDHO: BARI,
        QORYOOLEY: LOWER_SHABELLE,
        RAB_DHUURE: BAKOOL,
        SAAKOW: MIDDLE_JUBA,
        SABLAALE: LOWER_SHABELLE,
        SHEIKH: TOGDHEER,
        TALEEX: SOOL,
        TAYEEGLOW: BAKOOL,
        WAAJID: BAKOOL,
        WANLA_WEYN: LOWER_SHABELLE,
        XARARDHEERE: MUDUG,
        XUDUN: SOOL,
        XUDUR: BAKOOL,
        ZEYLAC: AWDAL
    }

    REGION_TO_STATE_MAP = {
        AWDAL: SOMALILAND,
        BAKOOL: SOUTH_WEST_STATE,
        BANADIR: BANADIR,
        BARI: PUNTLAND,
        BAY: SOUTH_WEST_STATE,
        GALGADUUD: GALMUDUG,
        GEDO: JUBBALAND,
        HIRAAN: HIR_SHABELLE,
        LOWER_JUBA: JUBBALAND,
        LOWER_SHABELLE: SOUTH_WEST_STATE,
        MIDDLE_JUBA: JUBBALAND,
        MIDDLE_SHABELLE: HIR_SHABELLE,
        MUDUG: GALMUDUG,
        NUGAAL: PUNTLAND,
        SANAAG: SOMALILAND,
        SOOL: SOMALILAND,
        TOGDHEER: SOMALILAND,
        WOQOOYI_GALBEED: SOMALILAND
    }

    STATE_TO_ZONE_MAP = {
        BANADIR: SCZ,
        GALMUDUG: SCZ,
        HIR_SHABELLE: SCZ,
        JUBBALAND: SCZ,
        PUNTLAND: NEZ,
        SOMALILAND: NWZ,
        SOUTH_WEST_STATE: SCZ
    }

    OPERATOR_TO_ZONE_MAP = {
        GOLIS: NEZ,
        HORMUD: SCZ,
        TELESOM: NWZ
    }

    DISTRICTS = list(DISTRICT_TO_REGION_MAP.keys())
    DISTRICTS.extend(CANONICAL_DISTRICT_MAP.keys())

    REGIONS = list(REGION_TO_STATE_MAP.keys())

    STATES = list(STATE_TO_ZONE_MAP.keys())

    ZONES = [NEZ, NWZ, SCZ]
