import shutil
import tempfile
import unittest
from os import path
from random import Random

from matplotlib.testing.compare import compare_images

from core_data_modules.analysis.mapping import mapping_utils, somalia_mapper

_IMAGE_TOLERANCE = 0.0000001


class TestKenyaMapper(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @staticmethod
    def generate_distributions(regions):
        # Generate a random assignment of participation to all the given administrative regions.
        # Sample from -30 to 100 then clamp to the range 0 to 100 to make sure there are plenty of regions with no
        # participation.
        rand = Random(1)
        return {r: max(0, rand.randint(-30, 100)) for r in regions}

    def test_export_somalia_region_frequencies_map(self):
        regions = mapping_utils.get_standard_geodata("somalia", "regions")["ADM1_AVF"]
        frequencies = self.generate_distributions(regions)

        file_path = path.join(self.test_dir, "regions.png")
        somalia_mapper.export_somalia_region_frequencies_map(frequencies, file_path)

        self.assertIsNone(compare_images(file_path, "tests/analysis/mapping/resources/somalia/regions.png", _IMAGE_TOLERANCE))

    def test_export_somalia_district_frequencies_map(self):
        regions = mapping_utils.get_standard_geodata("somalia", "districts")["ADM2_AVF"]
        frequencies = self.generate_distributions(regions)

        file_path = path.join(self.test_dir, "districts.png")
        somalia_mapper.export_somalia_district_frequencies_map(frequencies, file_path)

        self.assertIsNone(
            compare_images(file_path, "tests/analysis/mapping/resources/somalia/districts.png", _IMAGE_TOLERANCE))

    def test_export_mogadishu_sub_district_frequencies_map(self):
        regions = mapping_utils.get_standard_geodata("somalia", "mogadishu_sub_districts")["ADM3_AVF"]
        frequencies = self.generate_distributions(regions)

        file_path = path.join(self.test_dir, "mogadishu_sub_districts.png")
        somalia_mapper.export_mogadishu_sub_district_frequencies_map(frequencies, file_path)

        self.assertIsNone(
            compare_images(file_path, "tests/analysis/mapping/resources/somalia/mogadishu_sub_districts.png", _IMAGE_TOLERANCE))
