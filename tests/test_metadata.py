import unittest
import pandas as pd
from io import StringIO
from unittest.mock import patch
from mopp.modules.metadata import (
    autogenerate_metadata,
    _md_to_df,
    _validate_md,
    _df_to_dict,
    _validate_paired_end,
    _validate_multiomics,
)


class metadataTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch("mopp.modules.metadata.glob")
    def test_autogenerate_metadata(self, mock_glob):
        mock_glob.return_value = [
            "indir/sample1_metaG_R1.fastq.gz",
            "indir/sample2_metaG_R2.fastq.gz",
            "indir/sample3_metaRS_R1.fq.gz",
        ]

        df_obs = autogenerate_metadata("indir")
        expected_data = {
            "sample_name": [
                "indir/sample1_metaG_R1.fastq.gz",
                "indir/sample2_metaG_R2.fastq.gz",
                "indir/sample3_metaRS_R1.fq.gz",
            ],
            "identifier": ["sample1", "sample2", "sample3"],
            "omic": ["metaG", "metaG", "metaRS"],
            "strand": ["R1", "R2", "R1"],
        }
        df_exp = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(df_obs, df_exp)

    def test_validate_md_valid(self):
        test_df_valid = pd.DataFrame(
            {
                "sample_name": ["sample1", "sample2"],
                "identifier": ["id1", "id2"],
                "omic": ["metaRS", "metaT"],
                "strand": ["r1", "r2"],
            }
        )
        try:
            _validate_md(test_df_valid)
        except:
            self.fail(
                "_validate_md() raised SystemExit unexpectedly for valid metadata"
            )

    def test_validate_md_invalid_column_count(self):
        test_df_icc = pd.DataFrame(
            {
                "sample_name": ["sample1", "sample2"],
                "identifier": ["id1", "id2"],
                "omic": ["metaRS", "metaT"],
            }
        )
        with self.assertRaises(SystemExit):
            _validate_md(test_df_icc)

    def test_validate_md_invalid_column_names(self):
        test_df_icn = pd.DataFrame(
            {
                "sample_name": ["sample1", "sample2"],
                "identifiers": ["id1", "id2"],
                "omic": ["metaRS", "metaT"],
                "strand\t": ["r1", "r2"],
            }
        )
        with self.assertRaises(SystemExit):
            _validate_md(test_df_icn)

    def test_validate_md_invalid_omic_values(self):
        test_df_iov = pd.DataFrame(
            {
                "sample_name": ["sample1", "sample2"],
                "identifier": ["id1", "id2"],
                "omic": ["metars", "metaT"],
                "strand": ["r1", "r2"],
            }
        )
        with self.assertRaises(SystemExit):
            _validate_md(test_df_iov)

    def test_validate_md_invalid_duplicated_identifiers(self):
        test_df_idi = pd.DataFrame(
            {
                "sample_name": ["sample1", "sample2"],
                "identifier": ["id1", "id1"],
                "omic": ["metaRS", "metaRS"],
                "strand": ["r1", "r1"],
            }
        )
        with self.assertRaises(SystemExit):
            _validate_md(test_df_idi)

    def test_validate_md_invalid_paired(self):
        test_df_ip = pd.DataFrame(
            {
                "sample_name": ["sample1", "sample2"],
                "identifier": ["id1", "id1"],
                "omic": ["metaRS", "metaT"],
                "strand": ["r1", "r1"],
            }
        )
        with self.assertRaises(SystemExit):
            _validate_md(test_df_ip, paired=True)

    def test_validate_md_invalid_multiomics(self):
        test_df_im = pd.DataFrame(
            {
                "sample_name": ["sample1", "sample2"],
                "identifier": ["id1", "id1"],
                "omic": ["metaRS", "metaT"],
                "strand": ["r1", "r1"],
            }
        )
        with self.assertRaises(SystemExit):
            _validate_md(test_df_im, multiomics=True)

    def test_md_to_df(self):
        # use StringIO to simmulate a file object
        test_data = """sample_name\tidentifier\tomic\tstrand
        sample1\tid1\tmetaRS\tr1
        sample2\tid2\tmetaT\tr2
        """
        df = _md_to_df(StringIO(test_data))

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 4))
        self.assertListEqual(
            df.columns.tolist(),
            ["sample_name", "identifier", "omic", "strand"],
        )
        self.assertEqual(df["sample_name"].iloc[0], "sample1")

    def test_md_to_df_caps(self):
        # use StringIO to simmulate a file object
        test_data = """sample_name\tidentifier\tomic\tstrand
        sample1\tid1\tmetaRS\tR1
        sample2\tid2\tmetaT\tr2
        """
        df = _md_to_df(StringIO(test_data))
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 4))
        self.assertListEqual(
            df.columns.tolist(),
            ["sample_name", "identifier", "omic", "strand"],
        )
        self.assertEqual(df["sample_name"].iloc[0], "sample1")
        self.assertEqual(df["strand"].iloc[0], "r1")

    def test_df_to_dict(self):
        test_df = pd.DataFrame(
            {
                "sample_name": ["sample1", "sample2"],
                "identifier": ["id1", "id2"],
                "omic": ["metaRS", "metaT"],
                "strand": ["r1", "r2"],
            }
        )
        dict_obs = _df_to_dict(test_df)
        dict_exp = {
            "id1": {"metaRS": ["sample1"]},
            "id2": {"metaT": [-1, "sample2"]},
        }
        self.assertEqual(dict_obs, dict_exp)

    def test_valid_paired_end_valid(self):
        test_df_valid = pd.DataFrame(
            {
                "sample_name": ["sample1", "sample2", "sample3"],
                "identifier": ["id1", "id2", "id2"],
                "omic": ["metaRS", "metaT", "metaT"],
                "strand": ["r1", "r2", "r1"],
            }
        )
        try:
            _validate_paired_end(test_df_valid)
        except:
            self.fail(
                "_validate_paired_end() raised SystemExit unexpectedly for valid metadata"
            )

    def test_valid_paired_end_invalid(self):
        test_df_invalid = pd.DataFrame(
            {
                "sample_name": ["sample1", "sample2", "sample3"],
                "identifier": ["id1", "id2", "id3"],
                "omic": ["metaRS", "metaT", "metaG"],
                "strand": ["r1", "r2", "r1"],
            }
        )
        with self.assertRaises(SystemExit):
            _validate_paired_end(test_df_invalid)

    def test_valid_multiomics_valid(self):
        test_df_valid = pd.DataFrame(
            {
                "sample_name": ["sample1", "sample2", "sample3"],
                "identifier": ["id1", "id1", "id1"],
                "omic": ["metaRS", "metaT", "metaG"],
                "strand": ["r1", "r2", "r1"],
            }  # note that this does not check for r1/r2
        )
        try:
            _validate_multiomics(test_df_valid)
        except:
            self.fail(
                "_validate_multiomics() raised SystemExit unexpectedly for valid metadata"
            )

    def test_valid_multiomics_invalid(self):
        test_df_invalid = pd.DataFrame(
            {
                "sample_name": ["sample1", "sample2", "sample3"],
                "identifier": ["id1", "id1", "id1"],
                "omic": ["metaRS", "metaT", "metaT"],
                "strand": ["r1", "r2", "r1"],
            }
        )
        with self.assertRaises(SystemExit):
            _validate_multiomics(test_df_invalid)


if __name__ == "__main__":
    unittest.main()
