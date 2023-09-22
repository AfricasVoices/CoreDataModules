import shutil
import tempfile
import unittest
from os import path
from random import Random

from matplotlib.testing.compare import compare_images

from core_data_modules.analysis.mapping import kenya_mapper, mapping_utils

_IMAGE_TOLERANCE = 0.1


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
        rand = Random(0)
        return {r: max(0, rand.randint(-30, 100)) for r in regions}

    def test_export_kenya_constituencies_frequencies_map(self):
        constituencies = mapping_utils.get_standard_geodata("kenya", "constituencies")["ADM2_AVF"]
        frequencies = self.generate_distributions(constituencies)

        file_path = path.join(self.test_dir, "constituencies.png")
        kenya_mapper.export_kenya_constituencies_map(frequencies, file_path)

        self.assertIsNone(compare_images(file_path, "tests/analysis/mapping/resources/kenya/constituencies.png", _IMAGE_TOLERANCE))

    def test_export_kenya_counties_frequencies_map(self):
        counties = mapping_utils.get_standard_geodata("kenya", "counties")["ADM1_AVF"]
        frequencies = self.generate_distributions(counties)

        file_path = path.join(self.test_dir, "counties.png")
        kenya_mapper.export_kenya_counties_map(frequencies, file_path)
        self.assertIsNone(compare_images(file_path, "tests/analysis/mapping/resources/kenya/counties.png", _IMAGE_TOLERANCE))

        file_path = path.join(self.test_dir, "counties_filtered.png")
        kenya_mapper.export_kenya_counties_map(frequencies, file_path, region_filter=lambda county: county in {"siaya", "kakamega", "kisumu"})
        self.assertIsNone(compare_images(file_path, "tests/analysis/mapping/resources/kenya/counties_filtered.png", _IMAGE_TOLERANCE))
