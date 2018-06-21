import re

from core_data_modules.cleaners.codes import Codes
from core_data_modules.cleaners.regexes import Regex

from .patterns import Patterns
import numpy as np
import sys


class DemographicCleaner(object):
    @staticmethod
    def clean_with_patterns(text, patterns):
        """
        Attempts to clean a string by applying each of the provided regex patterns to the given text.
        
        The code associated with the first pattern to match is returned.

        :param text: Text to clean.
        :type text: str
        :param patterns: Dictionary of code/pattern pairs.
        :type patterns: dict of str -> str
        :return: Code for first matching pattern.
        :rtype: str
        """
        for code, pattern in patterns.items():
            if Regex.has_matches(text, pattern):
                # TODO: This follows what Dreams did, but do we really want to
                return code
        return Codes.NotCleaned

    @classmethod
    def clean_gender(cls, text):
        """
        Identifies the gender in the given string.

        >>> DemographicCleaner.clean_gender("KiUMe")
        'male'

        :param text: Text to clean.
        :type text: str
        :return: Codes.male, Codes.female, or None if no gender could be identified.
        :rtype: str
        """
        patterns = {
            Codes.male: Patterns.male,
            Codes.female: Patterns.female
        }

        return cls.clean_with_patterns(text, patterns)

    @classmethod
    def clean_number_units(cls, text):
        """
        Extracts a units-column number word from the given text, and converts that to an integer.

        >>> DemographicCleaner.clean_number_units("tano")
        5

        :param text: Text to clean.
        :type text: str
        :return: A number from 1-9 inclusive.
        :rtype: int
        """
        patterns = {
            1: Patterns.one,
            2: Patterns.two,
            3: Patterns.three,
            4: Patterns.four,
            5: Patterns.five,
            6: Patterns.six,
            7: Patterns.seven,
            8: Patterns.eight,
            9: Patterns.nine,
        }

        return cls.clean_with_patterns(text, patterns)

    @classmethod
    def clean_number_teens(cls, text):
        """
        Extract a "teens" number word from the given text.

        >>> DemographicCleaner.clean_number_teens("eleven")
        11

        :param text: Text to clean.
        :type text: str
        :return: A number from 11-19 inclusive.
        :rtype: int
        """
        patterns = {
            11: Patterns.eleven,
            12: Patterns.twelve,
            13: Patterns.thirteen,
            14: Patterns.fourteen,
            15: Patterns.fifteen,
            16: Patterns.sixteen,
            17: Patterns.seventeen,
            18: Patterns.eighteen,
            19: Patterns.nineteen
        }

        return cls.clean_with_patterns(text, patterns)

    @classmethod
    def clean_number_tens(cls, text):
        """
        Extract a tens-column number word from the given text, and converts that to an integer.

        >>> DemographicCleaner.clean_number_tens("arobaini")
        40

        :param text: Text to clean.
        :type text: str
        :return: 10, 20, 30, ..., 80, or 90.
        :rtype: int
        """
        patterns = {
            10: Patterns.ten,
            20: Patterns.twenty,
            30: Patterns.thirty,
            40: Patterns.forty,
            50: Patterns.fifty,
            60: Patterns.sixty,
            70: Patterns.seventy,
            80: Patterns.eighty,
            90: Patterns.ninety
        }

        return cls.clean_with_patterns(text, patterns)

    @staticmethod
    def replace_digit_like_characters(text):
        """
        Replaces letters which look like digits with the digits they look like.

        For example, the characters "o" and "O" are replaced with "0".

        :param text: Text to replace digit-like characters with digits.
        :type text: str
        :return: text with digit-like characters replaced
        :rtype: str
        """
        replacements = {
            "o": "0",
            "i": "1",
            "j": "1",
            "l": "1",
            "z": "2",
            "t": "7"
        }

        for target, replacement in replacements.items():
            text = text.replace(target, replacement)
            text = text.replace(target.upper(), replacement)
        
        return text

    @classmethod
    def clean_number_words(cls, text):
        """
        Extracts the number words in the given text and converts them to an integer.

        Extracts numbers in the range 1 to 99 inclusive.

        For example:
        >>> DemographicCleaner.clean_number_words("thirteen")
        13

        >>> DemographicCleaner.clean_number_words("seventy four")
        74

        :param text: Text to clean
        :type text: str
        :return: Extracted number
        :rtype: int | Codes.NotCleaned
        """
        cleaned_units = cls.clean_number_units(text)
        if cleaned_units == Codes.NotCleaned:
            cleaned_units = 0

        cleaned_teens = cls.clean_number_teens(text)
        if cleaned_teens == Codes.NotCleaned:
            cleaned_teens = 0
            
        cleaned_tens = cls.clean_number_tens(text)
        if cleaned_tens == Codes.NotCleaned:
            cleaned_tens = 0

        cleaned = cleaned_tens + cleaned_teens + cleaned_units

        if cleaned == 0:
            cleaned = Codes.NotCleaned

        return cleaned
    
    @classmethod
    def clean_number_digits(cls, text):
        """
        Extracts the digit (and digit-like characters e.g. 'o') from the given text and converts to an integer.

        >>> DemographicCleaner.clean_number_digits("I am 2O years old")
        '20'

        :param text: Text to clean
        :type text: str
        :return: Extracted number
        :rtype: str  TODO: Are we sure we don't want int?
        """
        text = cls.replace_digit_like_characters(text)

        matches = re.search(r"(\b\d{2}\b|\b\d\d\b)", text)  # TODO: This regex only extracts 2-digit numbers
        if matches:
            return matches.group(1).strip()
        else:
            return Codes.NotCleaned

    @classmethod
    def clean_number(cls, text):
        """
        Extracts the number from the given text from either digits or words.

        See clean_number_digits and clean_number_words.

        >>> DemographicCleaner.clean_number("40")
        '40'

        >>> DemographicCleaner.clean_number("seventy-six")
        76

        :param text: Text to clean
        :type text: str
        :return: Extracted number
        :rtype: str | int  # TODO: depends on which function is called eww.
        """
        cleaned_digits = cls.clean_number_digits(text)
        if cleaned_digits != Codes.NotCleaned:
            return cleaned_digits
        else:
            return cls.clean_number_words(text)

    @classmethod
    def clean_age(cls, text):
        return cls.clean_number(text)


# These are imported from the DREAMS project.
# TODO: Delete.
class Cleaners(object):
    '''
    Used to pull clean data from columns.
    Assumes pandas is loaded
    '''

    def __init__(self):
        self.rg = Regex()

    def first_clean_column(self, dataframe, column):
        '''
        Preprocessing text data. Make it all lower case. Replaces the
        punctuation with space.Replaces spaces with a single space. Removes
        trailing spaces at the beginning and end of the string.
        :param dataframe: the dataframe you'd like to act on
        :param column: string, column you'd like to clean
        '''
        dataframe[column] = dataframe[column].str.lower()
        dataframe[column] = dataframe[column].str.replace('[.\?!,]', ' ')
        dataframe[column] = dataframe[column].str.replace(r'\s{2,}', ' ')
        dataframe[column] = dataframe[column].str.rstrip()
        dataframe[column] = dataframe[column].str.lstrip()

    def use_regex(self, dataframe, column, regexer):
        '''
        Takes a column and checks it for a regex, creates a column with the
        suffix _clean that contains what that regex matches
        :param dataframe: the dataframe you'd like to act on
        :param column: string, column you'd like to clean
        :regexer: list, contains the regular expresion and what it should
        resolve to usually from the Regex class
        '''
        if column in dataframe.columns:
            clean_column = '{}_clean'.format(column)
            indexer = dataframe[column].str.contains(regexer[0], case=False)
            indexer = indexer == True
            dataframe.loc[indexer, clean_column] = regexer[1]
        else:
            sys.exit('{} is not a column in the dataframe'.format(column))

    def clean_age(self, dataframe, column):
        '''
        Get ages from columns and place them in new column.
        :param dataframe: the dataframe you'd like to act on
        :param column: string, column you'd like to clean
        '''
        # dealing with word numbers
        if column not in dataframe.columns:
            sys.exit('{} is not a column in the dataframe'.format(column))

        clean_column = '{}_clean'.format(column)
        ones_col = '{}_ones'.format(column)
        tens_col = '{}_tens'.format(column)
        ones_array = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
                      'eight', 'nine']
        teens_array = ['eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
                       'sixteen', 'seventeen', 'eighteen', 'nineteen']
        tens_array = ['ten', 'twenty', 'thirty', 'forty', 'fifty', 'sixty',
                      'seventy', 'eighty', 'ninety']

        for number in ones_array:
            regexer = self.rg.number_word_swa(number)
            indexer = dataframe[column].str.contains(regexer[0], case=False)
            indexer = indexer == True
            dataframe.loc[indexer, ones_col] = regexer[1]
        dataframe[ones_col] = dataframe[ones_col].fillna(0)

        for number in teens_array:
            regexer = self.rg.number_word_swa(number)
            indexer = dataframe[column].str.contains(regexer[0], case=False)
            indexer = indexer == True
            dataframe.loc[indexer, tens_col] = regexer[1]

        for number in tens_array:
            regexer = self.rg.number_word_swa(number)
            indexer = dataframe[column].str.contains(regexer[0], case=False)
            indexer = indexer == True
            dataframe.loc[indexer, tens_col] = regexer[1]
        dataframe[tens_col] = dataframe[ones_col].fillna(0)

        dataframe[clean_column] = dataframe[ones_col] + dataframe[tens_col]
        dataframe.loc[dataframe[clean_column] == 0, clean_column] = np.NaN
        del dataframe[ones_col]
        del dataframe[tens_col]

        # fixing letter numbers
        dataframe['holder'] = dataframe[column].str.replace('o', '0',
                                                            case=False)
        dataframe['holder'] = dataframe['holder'].str.replace('z', '2',
                                                              case=False)
        dataframe['holder'] = dataframe['holder'].str.replace('i|j|l', '1',
                                                              case=False)
        dataframe['holder'] = dataframe['holder'].str.replace('t', '7',
                                                              case=False)
        # extract ages
        pattern = r'(\b\d{2}\b|\b\d\d\b)'
        dataframe['holder'] = dataframe['holder'].str.extract(pattern,
                                                              expand=False)
        dataframe['holder'] = dataframe['holder'].str.strip()
        indexer = dataframe['holder'].notnull()
        dataframe.loc[indexer, clean_column] = dataframe['holder']
        del dataframe['holder']

    def clean_gender(self, dataframe, column):
        '''
        Get gender from column and place it in a new column
        :param dataframe: dataframe you'd like to act on
        :param column: string, column you'd like to clean
        '''
        if column not in dataframe.columns:
            sys.exit('{} is not a column in the dataframe'.format(column))
        for gender in ['f', 'm']:
            regexer = self.rg.gender(gender)
            self.use_regex(dataframe, column, regexer)

    def clean_yes_no(self, dataframe, column):
        '''
        Get yes/no from column and place it in a new column
        :param dataframe: dataframe you'd like to act on
        :param column: string, column you'd like to clean
        '''
        if column not in dataframe.columns:
            sys.exit('{} is not a column in the dataframe'.format(column))
        for response in ['n', 'y']:
            regexer = self.rg.yes_no(response)
            self.use_regex(dataframe, column, regexer)

    def clean_rural_urban(self, dataframe, column):
        '''
        Get yes/no from column and place it in a new column
        :param dataframe: dataframe you'd like to act on
        :param column: string, column you'd like to clean
        '''
        if column not in dataframe.columns:
            sys.exit('{} is not a column in the dataframe'.format(column))
        for place in ['rural', 'urban']:
            regexer = self.rg.rural_urban(place)
            self.use_regex(dataframe, column, regexer)
