from core_data_modules.cleaners import Codes, somali
from core_data_modules.cleaners.code_scheme import CodeScheme


class DemographicSchemes(object):
    YES_NO = CodeScheme.with_missing_codes([Codes.YES, Codes.NO])
    GENDER = CodeScheme.with_missing_codes([Codes.MALE, Codes.FEMALE])
    URBAN_RURAL = CodeScheme.with_missing_codes([Codes.URBAN, Codes.RURAL])
    DISTRICT = CodeScheme.with_missing_codes(somali.DemographicPatterns.somalia_districts.keys())
    AGE = CodeScheme.with_missing_codes([str(i) for i in range(1, 101)])
