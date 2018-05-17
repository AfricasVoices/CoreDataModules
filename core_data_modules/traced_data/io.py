import unicodecsv

from core_data_modules.util import SHAUtils, TextUtils


class TracedDataCodaIO(object):
    @staticmethod
    def dump(data, col, f):
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
                "id": SHAUtils.create_hash_id(TextUtils.clean_text(td[col])),
                "owner": SHAUtils.create_hash_id(td["URN"]),  # TODO: Use Contact UUID to operate on current pipeline.
                "data": TextUtils.remove_non_ascii(td[col])
            }

            writer.writerow(row)

        # Ensure the output file doesn't end with a blank line.
        # TODO: Fix in Coda? This is not the first case that this issue has caused us pain.
        # TODO: This may break on file-like objects that are not files, making this implementation of dump non-Pythonic.
        file_path = f.name
        f.close()
        with open(file_path, "r") as f:
            lines = f.readlines()
        with open(file_path, "w") as f:
            lines[-1] = lines[-1].strip()
            f.writelines([item for item in lines if len(item) > 0])

    @staticmethod
    def load(f):
        pass
