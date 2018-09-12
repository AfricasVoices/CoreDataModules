from core_data_modules.cleaners import somali


class Codes(object):
    TRUE = "true"
    FALSE = "false"

    MALE = "male"
    FEMALE = "female"

    YES = "yes"
    NO = "no"

    URBAN = "urban"
    RURAL = "rural"
    
    SOMALIA_DISTRICTS = somali.DemographicPatterns.somalia_districts.keys()
    MOGADISHU_DISTRICTS = [
        "mogadishu",
        "boondheere",
        "cabdiasis",
        "daynile",
        "dharkenley",
        "heliwa",
        "hodan",
        "hawl wadaag",
        "karaan",
        "shangaani",
        "shibis",
        "waaberi",
        "wadajir",
        "wardhiigleey",
        "xamar jajab",
        "xamar weyn",
        "yaaqshid"
    ]

    TRUE_MISSING = "NA"
    SKIPPED = "NS"
    NOT_LOGICAL = "NL"
    NOT_CODED = None  # TODO: Change to "NC"

    # Somali mobile phone network operators
    GOLIS = "golis"
    HORMUD = "hormud"
    NATIONLINK = "nationlink"
    SOMTEL = "somtel"
    TELESOM = "telesom"
