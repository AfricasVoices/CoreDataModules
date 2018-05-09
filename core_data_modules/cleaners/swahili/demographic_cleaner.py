from .regexes import Regex
import numpy as np
import sys


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
