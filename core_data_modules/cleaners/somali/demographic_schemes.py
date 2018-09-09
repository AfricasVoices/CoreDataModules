from core_data_modules.cleaners import Codes, somali
from core_data_modules.cleaners.code_scheme import CodeScheme


class DemographicSchemes(object):
    @staticmethod
    def yes_no(scheme_id=1, scheme_name="Yes/No", with_missing=True):
        return CodeScheme(scheme_id=scheme_id, scheme_name=scheme_name, add_codes_for_missing=with_missing,
                          code_names=[Codes.YES, Codes.NO])

    @staticmethod
    def gender(scheme_id=1, scheme_name="Gender", with_missing=True):
        return CodeScheme(scheme_id=scheme_id, scheme_name=scheme_name, add_codes_for_missing=with_missing,
                          code_names=[Codes.MALE, Codes.FEMALE])

    @staticmethod
    def urban_rural(scheme_id=1, scheme_name="Urban/Rural", with_missing=True):
        return CodeScheme(scheme_id=scheme_id, scheme_name=scheme_name, add_codes_for_missing=with_missing,
                          code_names=[Codes.URBAN, Codes.RURAL])

    @staticmethod
    def somalia_district(scheme_id=1, scheme_name="Somalia District", with_missing=True):
        return CodeScheme(scheme_id=scheme_id, scheme_name=scheme_name, add_codes_for_missing=with_missing,
                          code_names=somali.DemographicPatterns.somalia_districts.keys())

    @staticmethod
    def age(scheme_id=1, scheme_name="Age", with_missing=True):
        return CodeScheme(scheme_id=scheme_id, scheme_name=scheme_name, add_codes_for_missing=with_missing,
                          code_names=[str(i) for i in range(1, 101)])
