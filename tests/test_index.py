import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from pathlib import Path
from mopp.modules.index import (
    genome_extraction,
    _cov_filter,
    _cov_filter_write,
    _genome_extract,
    _build_db,
    _commands_generation_bt2build,
)


class TestGenomeExtraction(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path("test_output")
        self.temp_dir.mkdir(exist_ok=True)

        obs = {
            "genome_id": ["S1", "S2", "S3"],
            "covered": [15, 79, 32],
            "length": [10135, 6345, 15353],
            "percent_covered": [0.3, 0.2, 0.5],
        }
        self.cov_data = pd.DataFrame(obs)

        self.cov_file = self.temp_dir / "coverages.tsv"
        self.cov_data.to_csv(self.cov_file, sep="\t", index=False)

        self.ref_db = self.temp_dir / "ref_db.fna"
        with open(self.ref_db, "w") as f:
            f.write(">S1\nATGC\n>S2\nCGTA\n>S3\nGCTA\n")

        self.prefix = "test_prefix"
        self.nthreads = 4

    def tearDown(self):
        for item in self.temp_dir.iterdir():
            if item.is_file():
                item.unlink()
        self.temp_dir.rmdir()

    def test_cov_filter(self):
        cov_filtered, gotu_filtered = _cov_filter(str(self.cov_file), 0.25)
        self.assertEqual(len(cov_filtered), 2)  # Only S3 and S1 should pass
        self.assertListEqual(gotu_filtered.tolist(), ["S3", "S1"])

    @patch("mopp.modules.index.logger")
    def test_cov_filter_write(self, mock_logger):
        cov_filtered, gotu_filtered = _cov_filter(str(self.cov_file), 0.25)
        gotu_filtered_list = _cov_filter_write(
            cov_filtered, gotu_filtered, self.temp_dir, self.prefix
        )

        self.assertTrue((self.temp_dir / f"{self.prefix}_filtered_coverages.tsv").exists())
        self.assertTrue((self.temp_dir / f"{self.prefix}_filtered_gotu.txt").exists())

    def test_genome_extract(self):
        genome_ids = ["S1", "S3"]
        output_fna_file = _genome_extract(
            genome_ids, str(self.ref_db), str(self.temp_dir), self.prefix
        )

        self.assertTrue(Path(output_fna_file).exists())

        with open(output_fna_file, "r") as f:
            content = f.read()
        self.assertIn(">S1", content)
        self.assertIn(">S3", content)
        self.assertNotIn(">S2", content)

    @patch("mopp.modules.index.subprocess.Popen")
    @patch("mopp.modules.index.logger")
    def test_build_db(self, mock_logger, mock_popen):
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"output", b"")
        mock_popen.return_value = mock_process

        output_fna_file = self.temp_dir / f"{self.prefix}_filtered_genomes.fna"
        output_fna_file.touch() 
        _build_db(str(output_fna_file), str(self.temp_dir), self.prefix, self.nthreads)

        mock_popen.assert_called_once()


    def test_commands_generation_bt2build(self):
        output_fna_file = "test.fna"
        output_bt2index = Path("test_output")
        commands = _commands_generation_bt2build(
            output_fna_file, output_bt2index, self.prefix, self.nthreads
        )

        expected_commands = [
            "bowtie2-build",
            output_fna_file,
            f"{output_bt2index}/{self.prefix}",
            "--large-index",
            "--threads",
            str(self.nthreads),
        ]
        self.assertEqual(commands, expected_commands)

    @patch("mopp.modules.index._build_db")
    @patch("mopp.modules.index._genome_extract")
    @patch("mopp.modules.index._cov_filter_write")
    @patch("mopp.modules.index._cov_filter")
    @patch("mopp.modules.index.create_folder_without_clear")
    def test_genome_extraction(
        self,
        mock_create_folder,
        mock_cov_filter,
        mock_cov_filter_write,
        mock_genome_extract,
        mock_build_db,
    ):
        mock_cov_filter.return_value = (self.cov_data, pd.Series(["S1", "S3"]))
        mock_cov_filter_write.return_value = ["S1", "S3"]
        mock_genome_extract.return_value = str(
            self.temp_dir / f"{self.prefix}_filtered_genomes.fna"
        )

        genome_extraction(
            str(self.cov_file), 0.25, str(self.ref_db), str(self.temp_dir), self.prefix, self.nthreads
        )


        mock_cov_filter.assert_called_once_with(str(self.cov_file), 0.25)
        mock_cov_filter_write.assert_called_once()
        mock_genome_extract.assert_called_once()
        mock_build_db.assert_called_once()


if __name__ == "__main__":
    unittest.main()
