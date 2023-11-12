import click
from glob import glob
import time
import logging
from os import path
import os
import subprocess
import pandas as pd
from pandas.testing import assert_frame_equal

import unittest
#from mopp._defaults import (DESC_MD, DESC_INPUT)
from mopp.modules import trim
from mopp.modules import align
from mopp.modules import (load_metadata, md_to_dict, validate_metadata)
import logging

def tearDown(dir):
    # Clean up the temporary directory and its contents
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)



class Test(unittest.TestCase):

    def test_align_files(self):
        test_dict =  md_to_dict(load_metadata('./test/data/metadata.tsv'))

        trim.trim_files("./test/data","./test/out", md_to_dict(load_metadata("./test/data/metadata.tsv")))
        align.align_files("./test/out/trimmed", "./test/out",test_dict,'./wol_subset_index/wol_subset0.1_index')

        manual_metag_bow = "./test/data/out_manual/aligned/1-1_t2_metaG_cat_trimmed_WoL_subset.bow"
        manual_metag_sam = "./test/data/out_manual/aligned/1-1_t2_metaG_cat_trimmed_WoL_subset.sam"

        manual_metat_bow = "./test/data/out_manual/aligned/1-1_t2_metaT_cat_trimmed_WoL_subset.bow"
        manual_metat_sam = "./test/data/out_manual/aligned/1-1_t2_metaT_cat_trimmed_WoL_subset.sam"

        manual_metars_bow = "./test/data/out_manual/aligned/1-1_t2_metaRS_cat_trimmed_WoL_subset.bow"
        manual_metars_sam = "./test/data/out_manual/aligned/1-1_t2_metaRS_cat_trimmed_WoL_subset.sam"


        test_metag_bow = "./test/out/aligned/1-1_t2_metaG_cat_trimmed_WoL_subset.bow"
        test_metag_sam = "../test/out/aligned/1-1_t2_metaG_cat_trimmed_WoL_subset.sam"

        test_metat_bow = "./test/out/aligned/1-1_t2_metaT_cat_trimmed_WoL_subset.bow"
        test_metat_sam = "./test/out/aligned/1-1_t2_metaT_cat_trimmed_WoL_subset.sam"

        test_metars_bow = "./test/out/aligned/1-1_t2_metaRS_cat_trimmed_WoL_subset.bow"
        test_metars_sam = "./test/out/aligned/1-1_t2_metaRS_cat_trimmed_WoL_subset.sam"

        self.assertEqual(manual_metag_bow, test_metag_bow)
        self.assertEqual(manual_metag_sam, test_metag_sam)

        self.assertEqual(manual_metat_bow, test_metat_bow)
        self.assertEqual(manual_metat_sam, test_metat_sam)

        self.assertEqual(manual_metars_bow, test_metars_bow)
        self.assertEqual(manual_metars_sam, test_metars_sam)



    def test_run_align(self):
        test_dict =  md_to_dict(load_metadata('./test/data/metadata.tsv'))
        trim._run_trim_paired("./test/data/1-1_t2_metaG_S121_L004_R1_001.250k.fastq.gz", "./test/data/1-1_t2_metaG_S121_L004_R2_001.250k.fastq.gz", "./test/out")
        trim._concat_paired('./test/out', test_dict)
        align._run_align("./test/out/1-1_t2_metaG_cat_trimmed.fq.gz", './test/out/', './wol_subset_index/wol_subset0.1_index')

        test_bow = "./test/out/1-1_t2_metaG_cat_trimmed_WoL_subset.bow"
        test_sam = "./test/out/1-1_t2_metaG_cat_trimmed_WoL_subset.sam"

        manual_alignment_bow = "./test/data/out_manual/aligned/1-1_t2_metaG_cat_trimmed_WoL_subset.bow"
        manual_alignment_sam = "./test/data/out_manual/aligned/1-1_t2_metaG_cat_trimmed_WoL_subset.sam"
        
        self.assertEqual(test_bow, manual_alignment_bow)
        self.assertEqual(test_sam, manual_alignment_sam)

        tearDown("./test/out")


    ### METADATA FUNCTIONS
    """
    def test_load_metadatafile(self):

        test_df = load_metadata('./test/data/metadata.tsv')

        expected_data = pd.DataFrame({
            "sample_name": ["1-1_t2_metaRS_S13_L004_R1_001.250k.fastq.gz", 
                     "1-1_t2_metaT_S37_L004_R2_001.250k.fastq.gz", 
                     "1-1_t2_metaT_S37_L004_R1_001.250k.fastq.gz",
                     "1-1_t2_metaG_S121_L004_R2_001.250k.fastq.gz",
                     "1-1_t2_metaG_S121_L004_R1_001.250k.fastq.gz"],

            "identifier" : ["1-1_t2",
                            "1-1_t2",
                            "1-1_t2",
                            "1-1_t2",
                            "1-1_t2"],

            "omic": ["metaRS",
                     "metaT",
                     "metaT",
                     "metaG",
                     "metaG"],

            "strand": ["R1",
                       "R2",
                       "R1",
                       "R2",
                       "R1"]
        })
        expected_data = expected_data.set_index("sample_name")
        assert_frame_equal(test_df, expected_data)
        tearDown("./test/out")

    def test_md_to_dict(self):

        test_dict =  md_to_dict(load_metadata('./test/data/metadata.tsv'))
        
        expected_dict = {'1-1_t2': 
                    {'metaG': ['1-1_t2_metaG_S121_L004_R1_001.250k.fastq.gz',
                                '1-1_t2_metaG_S121_L004_R2_001.250k.fastq.gz'],
                     'metaT': ['1-1_t2_metaT_S37_L004_R1_001.250k.fastq.gz', 
                               '1-1_t2_metaT_S37_L004_R2_001.250k.fastq.gz'], 
                     'metaRS': ['1-1_t2_metaRS_S13_L004_R1_001.250k.fastq.gz']
        }}
        
        self.assertDictEqual(test_dict, expected_dict)
        tearDown("./test/out")

    def test_validate_metadata(self):

        test_dict =  md_to_dict(load_metadata('./test/data/metadata.tsv'))

        test_validation = validate_metadata(test_dict)
        expected_validation = True

        self.assertEqual(test_validation, expected_validation)
        tearDown("./test/out")


    ### METADATA END
        
    ### TRIM FUNCTIONS

    def test_concat_paired(self):

        test_dict =  md_to_dict(load_metadata('./test/data/metadata.tsv'))
        trim._run_trim_metars("./test/data/1-1_t2_metaRS_S13_L004_R1_001.250k.fastq.gz", "./test/out")
        trim._run_trim_paired("./test/data/1-1_t2_metaG_S121_L004_R1_001.250k.fastq.gz", "./test/data/1-1_t2_metaG_S121_L004_R2_001.250k.fastq.gz", "./test/out")

        trim._concat_paired("./test/out", test_dict)

        cat_file1 = './test/out/trimmed/1-1_t2_metaG_cat_trimmed.fq.gz'
        cat_file2 = './test/data/out_manual/trimmed/1-1_t2_metaG_cat_trimmed.fq.gz'

        decompressed_file1 = subprocess.check_output(['zcat', cat_file1], universal_newlines=True)
        decompressed_file2 = subprocess.check_output(['zcat', cat_file2], universal_newlines=True)
        
        self.assertEqual(decompressed_file1, decompressed_file2)

        cat_file3 = './test/out/trimmed/1-1_t2_metaRS_cat_trimmed.fq.gz'
        cat_file4 = './test/data/out_manual/trimmed/1-1_t2_metaRS_cat_trimmed.fq.gz'

        decompressed_file3 = subprocess.check_output(['zcat', cat_file3], universal_newlines=True)
        decompressed_file4 = subprocess.check_output(['zcat', cat_file4], universal_newlines=True)
        
        self.assertEqual(decompressed_file3, decompressed_file4)

        cat_file5 = './test/out/trimmed/1-1_t2_metaT_cat_trimmed.fq.gz'
        cat_file6 = './test/data/out_manual/trimmed/1-1_t2_metaT_cat_trimmed.fq.gz'

        decompressed_file5 = subprocess.check_output(['zcat', cat_file5], universal_newlines=True)
        decompressed_file6 = subprocess.check_output(['zcat', cat_file6], universal_newlines=True)
        
        self.assertEqual(decompressed_file5, decompressed_file6)
        tearDown("./test/out")

        




    
    def test_run_trim_metars(self):

        trim._run_trim_metars("./test/data/1-1_t2_metaRS_S13_L004_R1_001.250k.fastq.gz", "./test/out")
        fastqz_file1 = './test/out/1-1_t2_metaRS_S13_L004_R1_001.250k_trimmed.fq.gz'
        fastqz_file2 = './test/data/out_manual/trimmed/1-1_t2_metaRS_S13_L004_R1_001.250k_trimmed.fq.gz'


        decompressed_file1 = subprocess.check_output(['zcat', fastqz_file1], universal_newlines=True)
        decompressed_file2 = subprocess.check_output(['zcat', fastqz_file2], universal_newlines=True)

        self.assertEqual(decompressed_file1, decompressed_file2)
        tearDown("./test/out")

    def test_run_trim_paired(self):
        
        trim._run_trim_paired("./test/data/1-1_t2_metaG_S121_L004_R1_001.250k.fastq.gz", "./test/data/1-1_t2_metaG_S121_L004_R2_001.250k.fastq.gz", "./test/out")
        
        orig_1 = './test/out/1-1_t2_metaG_S121_L004_R1_001.250k_val_1.fq.gz'
        orig_2 = './test/out/1-1_t2_metaG_S121_L004_R2_001.250k_val_2.fq.gz'
        
        fastqz_file1 = './test/data/out_manual/trimmed/1-1_t2_metaG_S121_L004_R1_001.250k_val_1.fq.gz'
        fastqz_file2 = './test/data/out_manual/trimmed/1-1_t2_metaG_S121_L004_R2_001.250k_val_2.fq.gz'

        decompressed_file1 = subprocess.check_output(['zcat', orig_1], universal_newlines=True)
        decompressed_file2 = subprocess.check_output(['zcat', orig_2], universal_newlines=True)

        decompressed_file3 = subprocess.check_output(['zcat', fastqz_file1], universal_newlines=True)
        decompressed_file4 = subprocess.check_output(['zcat', fastqz_file2], universal_newlines=True)
        
        self.assertEqual(decompressed_file1, decompressed_file3)
        self.assertEqual(decompressed_file2, decompressed_file4)
        tearDown("./test/out")




    def test_trim_files(self):

        trim.trim_files("./test/data","./test/out", load_metadata.md_to_dict(load_metadata.load_metadatafile("./test/data/metadata.tsv")))

        orig_1 = './test/out/trimmed/1-1_t2_metaG_S121_L004_R1_001.250k_val_1.fq.gz'
        orig_2 = './test/out/trimmed/1-1_t2_metaG_S121_L004_R2_001.250k_val_2.fq.gz'
        orig_3 = './test/out/trimmed/1-1_t2_metaRS_S13_L004_R1_001.250k_trimmed.fq.gz'
        orig_4 = './test/out/trimmed/1-1_t2_metaT_S37_L004_R1_001.250k_val_1.fq.gz'
        orig_5 = './test/out/trimmed/1-1_t2_metaT_S37_L004_R2_001.250k_val_2.fq.gz'

        fastqz_file1 = './test/data/out_manual/trimmed/1-1_t2_metaG_S121_L004_R1_001.250k_val_1.fq.gz'
        fastqz_file2 = './test/data/out_manual/trimmed/1-1_t2_metaG_S121_L004_R2_001.250k_val_2.fq.gz'
        fastqz_file3 = './test/data/out_manual/trimmed/1-1_t2_metaRS_S13_L004_R1_001.250k_trimmed.fq.gz'
        fastqz_file4 = './test/data/out_manual/trimmed/1-1_t2_metaT_S37_L004_R1_001.250k_val_1.fq.gz'
        fastqz_file5 = './test/data/out_manual/trimmed/1-1_t2_metaT_S37_L004_R2_001.250k_val_2.fq.gz'

        decompressed_file1 = subprocess.check_output(['zcat', orig_1], universal_newlines=True)
        decompressed_file2 = subprocess.check_output(['zcat', orig_2], universal_newlines=True)
        decompressed_file3 = subprocess.check_output(['zcat', orig_3], universal_newlines=True)
        decompressed_file4 = subprocess.check_output(['zcat', orig_4], universal_newlines=True)
        decompressed_file5 = subprocess.check_output(['zcat', orig_5], universal_newlines=True)
        decompressed_file6 = subprocess.check_output(['zcat', fastqz_file1], universal_newlines=True)
        decompressed_file7 = subprocess.check_output(['zcat', fastqz_file2], universal_newlines=True)
        decompressed_file8 = subprocess.check_output(['zcat', fastqz_file3], universal_newlines=True)
        decompressed_file9 = subprocess.check_output(['zcat', fastqz_file4], universal_newlines=True)
        decompressed_file10 = subprocess.check_output(['zcat', fastqz_file5], universal_newlines=True)

        
        self.assertEqual(decompressed_file1, decompressed_file6)
        self.assertEqual(decompressed_file2, decompressed_file7)
        self.assertEqual(decompressed_file3, decompressed_file8)
        self.assertEqual(decompressed_file4, decompressed_file9)
        self.assertEqual(decompressed_file5, decompressed_file10)
        tearDown("./test/out")
        tearDown("./test/out/trimmed")


    ### TRIM FUNCTIONS END
"""

if __name__ == '__main__':
    tearDown("./test/out")
    unittest.main()
