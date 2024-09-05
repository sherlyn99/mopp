import unittest
import pandas as pd
from io import StringIO
from mopp.modules.metadata import _md_to_df, _validate_md, _df_to_dict


class metadataTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

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


if __name__ == "__main__":
    unittest.main()
