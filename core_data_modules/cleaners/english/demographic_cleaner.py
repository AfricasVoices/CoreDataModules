from core_data_modules.cleaners.codes import Codes


class DemographicCleaner(object):
    @staticmethod
    def clean_gender(text):
        """
        Converts a string describing gender to either man, woman, or Codes.NOT_CODED.

        :param text: Text to be cleaned.
        :return: Codes.MAN if man/male, Codes.Woman if woman/female, or Codes.NOT_CODED if the gender could not automatically be
                 identified.
        """
        text = text.lower()
        if text == "m" or text == "male" or text == "man":
            return Codes.MAN
        elif text == "f" or text == "female" or text == "woman":
            return Codes.WOMAN
        else:
            return Codes.NOT_CODED
