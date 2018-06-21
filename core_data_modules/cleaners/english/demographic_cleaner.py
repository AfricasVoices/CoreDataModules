from core_data_modules.cleaners.codes import Codes


class DemographicCleaner(object):
    @staticmethod
    def clean_gender(text):
        """
        Converts a string describing gender to either male, female, or None.

        :param text: Text to be cleaned.
        :return: Codes.male if male, Codes.female if female, or Codes.NotCleaned if the gender could not automatically be
                 identified.
        """
        text = text.lower()
        if text == "m" or text == "male" or text == "man":
            return Codes.male
        elif text == "f" or text == "female" or text == "woman":
            return Codes.female
        else:
            return Codes.NotCleaned
