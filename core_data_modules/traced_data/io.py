import time

import six
import unicodecsv
from core_data_modules import Metadata

from core_data_modules.util import SHAUtils, TextUtils


class TracedDataCodaIO(object):
    @staticmethod
    def export_coda(data, key, f):
        """
        Exports a "column" from a collection of TracedData objects to a file in Coda's data format.

        :param data: TracedData objects to export data to Coda from.
        :type data: iterable of TracedData
        :param key: The key in each TracedData object which should have its values exported.
        :type key: str
        :param f: File to export to, opened in 'wb' mode.
        :type f: file-like
        """
        headers = [
            "id", "owner", "data",
            "timestamp", "schemeId", "schemeName",
            "deco_codeValue", "deco_codeId", "deco_confidence", "deco_manual", "deco_timestamp", "deco_author"
        ]

        dialect = unicodecsv.excel
        dialect.delimiter = ";"

        writer = unicodecsv.DictWriter(f, fieldnames=headers, dialect=dialect, lineterminator="\n")
        writer.writeheader()

        for td in data:
            row = {
                "id": SHAUtils.create_hash_id(TextUtils.clean_text(td[key]).replace(" ", "")),

                # TODO: Use Contact UUID to operate on current pipeline.
                "owner": SHAUtils.create_hash_id(td["URN"]),

                # TODO: Data goes through a different cleaning process than id. This means messages which are identical
                # TODO: in all but case and whitespace will have the same id, breaking Coda.
                "data": TextUtils.remove_non_ascii(td[key])
            }

            writer.writerow(row)

        # Ensure the output file doesn't end with a blank line.
        # TODO: Fix in Coda? This is not the first case that this issue has caused us pain.
        # TODO: Reliance on f.name will break some file-like arguments which are not files.s
        file_path = f.name
        f.close()
        with open(file_path, "r") as f:
            lines = f.readlines()
        with open(file_path, "w") as f:
            lines[-1] = lines[-1].strip()
            f.writelines([item for item in lines if len(item) > 0])

    @staticmethod
    def import_coda(data, key_to_code, key_of_coded, f):
        """
        Codes a "column" of a collection of TracedData objects by looking up each value for that column in a coded
        Coda data file, and assigning the coded values to a specified column.

        :param data: TracedData objects to append import data into.
        :type data: iterable of TracedData
        :param key_to_code: Key of TracedData objects which should be coded.
        :type key_to_code: str
        :param key_of_coded: Key to write coded data to.
        :type key_of_coded: str
        :param f: Coda data file to import codes from.
        :type f: file-like
        :return: TracedData objects with Coda data appended
        :rtype: generator of TracedData
        """
        # TODO: I think this function is going to assume that there is only one code scheme...

        csv = unicodecsv.DictReader(f, delimiter=";")

        # Remove rows which still haven't been coded.
        coded = list(filter(lambda row: row["deco_codeValue"] != "", csv))

        for td in data:
            code = "NC"

            # TODO: Cleaning here is calling strip, which export does not.
            # TODO: Also, this mode of cleaning is called a lot. Refactor into a TextUtils method?
            td_id = SHAUtils.create_hash_id(TextUtils.clean_text(td[key_to_code]).strip().replace(" ", ""))
            td_text = td[key_to_code]
            td_cleaned_text = TextUtils.remove_non_ascii(TextUtils.clean_text(td_text).strip().replace(" ", ""))

            for row in coded:
                row_id = row["id"]
                row_text = row["data"]
                row_cleaned_text = TextUtils.remove_non_ascii(TextUtils.clean_text(row_text).strip().replace(" ", ""))

                if td_text != "nan":  # TODO: Aren't there other ways of being NaN? e.g. NaN and np.nan?
                    # TODO Why would one of these tests be true and the other not?
                    if str(row_id) != str(td_id) and td_cleaned_text != row_cleaned_text:
                        continue

                    # TODO: Really do this to Coda codes? This might be surprising to users of Coda who used e.g. upper
                    # TODO: case in their code names.
                    code = TextUtils.remove_non_ascii(row["deco_codeValue"].strip()).lower()
                    
            if code == "NC" or code == "non_relevant":
                pass  # TODO

            if code == "non-relevant":  # TODO: This is "-" separated but last time it was "_" separated
                code = "NC_cleared"

            # TODO: No idea what this is about.
            try:
                if str(td_text).lower() == 'haa waaa laga helaa':
                    print('key at from id', code)
            except:
                pass

            # TODO: Retrieve user/source from somewhere.
            td.append_data({key_of_coded: code}, Metadata("user", "coda_import", time.time()))

            yield td

    def _cash_code(self):
        coded_followup = self.coded_practice_files[followup]

        # id = create_hashid(asciify(text).lower().strip())
        code = 'NC'
        # code_columns = ['code', 'district', 'gender', 'idp', 'urban_rural', 'nomad', 'deco_codevalue', 'reason',
        #                 'reason_1', 'reason_2', 'code 1', 'code 2', 'code 3', 'relevant', 'yes/no']
        # cleaned_text = self.asciify(self.clean_text(text).strip().replace(' ', ''))
        # id = self.create_hashid(cleaned_text)
        # for row in coded_followup:
        #     id_from_file = row['id']
        #     cleaned_text_from_file = self.asciify(self.clean_text(row['data']).strip().replace(' ', ''))
        #     # cleaned_text_from_file = self.clean_text(row['text']).replace(' ', '')
        #     if text != 'nan':
        #         if str(id) != str(id_from_file) and cleaned_text != cleaned_text_from_file:
        #             continue
        #         for column in row.keys():
        #             if column.lower() in code_columns:
        #                 if len(row[column]) > 0:
        #                     print(column)
        #                     code = self.asciify(row[column].strip()).lower()
        #                     self.practices_and_codes[followup].add(row[column].strip())

        if code == 'NC' or code == 'non_relevant':
            for coded_file in self.coded_practice_files.values():
                for row in coded_file:
                    id_from_file = row['id']
                    cleaned_text_from_file = self.asciify(self.clean_text(row['data']).strip().replace(' ', ''))
                    # cleaned_text_from_file = self.clean_text(row['text']).replace(' ', '')
                    if text != 'nan':
                        if str(id) != str(id_from_file) and cleaned_text != cleaned_text_from_file:
                            continue
                        for column in row.keys():
                            if column.lower() in code_columns:
                                if len(row[column]) > 0:
                                    code = self.asciify(row[column].strip()).lower()
        if code == 'non-relevant':
            code = 'NC_cleared'
        try:
            if str(text).lower() == 'haa waaa laga helaa':
                print
                'key at from id', code
        except:
            pass
        return code


        files = {os.path.basename(filename).split('.')[0]: open(os.path.join(directory, filename), 'r') for filename in
                 filenames}
        coded_practice_files = {filename: list(unicodecsv.DictReader(f, delimiter=';')) for filename, f in
                                files.items()}
        print('opened coded practice files')
        for f in files.values():
            f.close()

