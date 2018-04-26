class DemographicCleaner:

    def __init__(self):
        pass

    @staticmethod
    def clean_gender(string):
        """
        Converts a string describing gender to M, F, or NC.
        :param string: Text to be cleaned.
        :return: "M" if male, "F" if female, "NC" if gender could not automatically be identified.
        """
        string = string.lower()
        if string == "m" or string == "male" or string == "man":
            return "M"
        elif string == "f" or string == "female" or string == "woman":
            return "F"
        else:
            return "NC"
