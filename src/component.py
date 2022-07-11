'''
COMPONENT INFO

'''
import csv
import sys
import logging

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

from psc_konvertor import PscKonvertor

# configuration variables
KEY_COLUMN_ZIP = 'column_psc'
KEY_COLUMN_DISTRICT = 'column_district'
KEY_COLUMN_COUNTY = 'column_county'

REQUIRED_PARAMETERS = [KEY_COLUMN_ZIP]
REQUIRED_IMAGE_PARS = []


class Component(ComponentBase):
    def __init__(self):
        super().__init__()

    def run(self):
        self.validate_configuration_parameters(REQUIRED_PARAMETERS)
        self.validate_image_parameters(REQUIRED_IMAGE_PARS)
        params = self.configuration.parameters

        input_table_defs = self.get_input_tables_definitions()
        if len(input_table_defs) == 0:
            logging.error("Table mapping with at least one entry is required")
            sys.exit(1)

        for index in range(len(input_table_defs)):
            SOURCE_FILE_PATH = input_table_defs[index].full_path
            RESULT_FILENAME = self.configuration.tables_output_mapping[index]['source']

            out_table = self.create_out_table_definition(RESULT_FILENAME)
            self.write_manifest(out_table)

            RESULT_FILE_PATH = out_table.full_path

            with open(SOURCE_FILE_PATH, 'rt') as input, open(RESULT_FILE_PATH, 'wt') as out:
                reader = csv.DictReader(input, dialect='kbc')
                new_columns = reader.fieldnames

                if not (params[KEY_COLUMN_ZIP] in new_columns):
                    logging.error("Column with ZIP codes was not found")
                    sys.exit(1)

                if params.get(KEY_COLUMN_COUNTY, None) is not None:
                    new_columns.append(params[KEY_COLUMN_COUNTY])
                if params.get(KEY_COLUMN_DISTRICT, None) is not None:
                    new_columns.append(params[KEY_COLUMN_DISTRICT])

                writer = csv.DictWriter(out, fieldnames=new_columns, dialect='kbc')
                writer.writeheader()

                def _unify_zip_code(zip_code):
                    try:
                        return int(zip_code.replace(" ", ""))
                    except Exception:
                        return None

                zip_convertor = PscKonvertor()
                for row in reader:
                    zip_code = _unify_zip_code(row[params[KEY_COLUMN_ZIP]])

                    county = None
                    district = None

                    if zip_code:
                        try:
                            district = zip_convertor.psc2okres(zip_code)
                            county = zip_convertor.psc2kraj(zip_code)
                        except KeyError:
                            logging.warning("ZIP Code '%s' was not found in database" % (zip_code))

                    if params.get(KEY_COLUMN_COUNTY, None) is not None:
                        row[params[KEY_COLUMN_COUNTY]] = county
                    if params.get(KEY_COLUMN_DISTRICT, None) is not None:
                        row[params[KEY_COLUMN_DISTRICT]] = district

                    writer.writerow(row)


if __name__ == "__main__":
    try:
        comp = Component()
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
