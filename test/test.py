import unittest
import pandas as pd
from pathlib import Path

from mopp.modules.indexdb import _genome_filter

class TestIndexdb(unittest.TestCase):

    def setUp(self):
        # create tmp dir for testing
        self.test_dir = Path('./test/out/indexdb')
        self.test_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        # clean up tmp dir after use
        for file in self.test_dir.glob('*'):
            file.unlink()
        self.test_dir.rmdir()
    
    def test_genome_filter(self):
        test_cov = "./test/data/calculate_coverages.tsv"
        test_cutoff = .95
        test_outdir = self.test_dir
        test_prefix = "test1"
        gotu_filtered = _genome_filter(test_cov,
                                       test_cutoff,
                                       test_outdir,
                                       test_prefix)
        # check return values
        assert gotu_filtered == ['G001283625','G000438035']
        # check if expected files were generated
        expected_cov_file = self.test_dir/f'{test_prefix}_filtered_coverages.tsv'
        expected_gotu_file = self.test_dir/f'{test_prefix}_filtered_gotu.txt'
        self.assertTrue(expected_cov_file.is_file())
        self.assertTrue(expected_gotu_file.is_file())


if __name__ == '__main__':
    unittest.main()
