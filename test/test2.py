import io
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
from mopp.modules.metadata import (
    _validate_metadata,
    _md_to_dict,
)
from mopp.modules.align import _commands_generation_bowtie2
from mopp.modules.coverages import _commands_generation_coverages
from mopp.modules.index import _cov_filter, _commands_generation_bt2build
from mopp.modules.features import (
    _commands_generation_woltka,
    _commands_stratification_generation_woltka,
)


class Test(unittest.TestCase):
    # module: metadata
    def test_validate_metadata(self):
        # md_df with correct format
        test_md_df = pd.DataFrame(
            {
                "sample_name": [
                    "1-1_t2_metaRS_S13_L004_R1_001.250k.fastq.gz",
                    "1-1_t2_metaT_S37_L004_R2_001.250k.fastq.gz",
                    "1-1_t2_metaT_S37_L004_R1_001.250k.fastq.gz",
                    "1-1_t2_metaG_S121_L004_R2_001.250k.fastq.gz",
                    "1-1_t2_metaG_S121_L004_R1_001.250k.fastq.gz",
                ],
                "identifier": ["1-1_t2", "1-1_t2", "1-1_t2", "1-1_t2", "1-1_t2"],
                "omic": ["metaRS", "metaT", "metaT", "metaG", "metaG"],
                "strand": ["R1", "R2", "R1", "R2", "R1"],
            }
        )

        expected_md_df = pd.DataFrame(
            {
                "sample_name": [
                    "1-1_t2_metaRS_S13_L004_R1_001.250k.fastq.gz",
                    "1-1_t2_metaT_S37_L004_R2_001.250k.fastq.gz",
                    "1-1_t2_metaT_S37_L004_R1_001.250k.fastq.gz",
                    "1-1_t2_metaG_S121_L004_R2_001.250k.fastq.gz",
                    "1-1_t2_metaG_S121_L004_R1_001.250k.fastq.gz",
                ],
                "identifier": ["1-1_t2", "1-1_t2", "1-1_t2", "1-1_t2", "1-1_t2"],
                "omic": ["metaRS", "metaT", "metaT", "metaG", "metaG"],
                "strand": ["R1", "R2", "R1", "R2", "R1"],
                "label": [
                    "1-1_t2|metaRS|R1",
                    "1-1_t2|metaT|R2",
                    "1-1_t2|metaT|R1",
                    "1-1_t2|metaG|R2",
                    "1-1_t2|metaG|R1",
                ],
            }
        )
        actual_md_df = _validate_metadata(test_md_df)
        assert_frame_equal(expected_md_df, actual_md_df)

        # md_df with incorrect number of columns
        test_md_df_wrongncol = pd.DataFrame(
            {
                "sample_name": [
                    "1-1_t2_metaRS_S13_L004_R1_001.250k.fastq.gz",
                    "1-1_t2_metaT_S37_L004_R2_001.250k.fastq.gz",
                    "1-1_t2_metaT_S37_L004_R1_001.250k.fastq.gz",
                    "1-1_t2_metaG_S121_L004_R2_001.250k.fastq.gz",
                    "1-1_t2_metaG_S121_L004_R1_001.250k.fastq.gz",
                ],
                "identifier": ["1-1_t2", "1-1_t2", "1-1_t2", "1-1_t2", "1-1_t2"],
                "omic": ["metaRS", "metaT", "metaT", "metaG", "metaG"],
            }
        )
        with self.assertRaises(ValueError):
            _validate_metadata(test_md_df_wrongncol)

    def test_md_to_dict(self):
        test_md_df = pd.DataFrame(
            {
                "sample_name": [
                    "sample1_R1",
                    "sample1_R2",
                    "sample2_R1",
                    "sample2_R2",
                    "sample3",
                ],
                "identifier": ["id1", "id1", "id2", "id2", "id3"],
                "omic": ["metaG", "metaG", "metaT", "metaT", "metaRS"],
                "strand": ["r1", "r2", "r1", "r2", "r1"],
            }
        )
        expected_dict = {
            "id1": {
                "metaG": ["sample1_R1", "sample1_R2"],
                "metaT": [-1, -1],
                "metaRS": [-1],
            },
            "id2": {
                "metaG": [-1, -1],
                "metaT": ["sample2_R1", "sample2_R2"],
                "metaRS": [-1],
            },
            "id3": {"metaG": [-1, -1], "metaT": [-1, -1], "metaRS": ["sample3"]},
        }
        actual_dict = _md_to_dict(test_md_df)
        self.assertEqual(expected_dict, actual_dict)

    # module: align
    def test_commands_generation_bowtie2(self):
        filepath = "./test/data/out2/cat/1-1_t2_metaG_trimmed.fq.gz"
        identifier = "1-1_t2_metaG_trimmed"
        suffix = "WoL30"
        outdir = "./test/data/out2/aligned"
        INDEX = "./test/data/wol_subset_index/wol_subset0.1_index"
        nthreads = 4

        expected_commands = "bowtie2 -U ./test/data/out2/cat/1-1_t2_metaG_trimmed.fq.gz -x ./test/data/wol_subset_index/wol_subset0.1_index -p 4 --no-unal --no-head -S test/data/out2/aligned/samfiles/1-1_t2_metaG_trimmed_WoL30.sam 2> test/data/out2/aligned/bowfiles/1-1_t2_metaG_trimmed_WoL30.bow"
        actual_commands = " ".join(
            _commands_generation_bowtie2(
                filepath, identifier, suffix, outdir, INDEX, nthreads
            )
        )

        self.assertEqual(expected_commands, actual_commands)

    # module: coverages
    def test_commands_generation_zebra(self):
        zebra_path = "/home/y1weng/zebra_filter"
        indir = "./test/data/out2/aligned/"
        outdir = "./test/data/out2"

        expected_commands = "python /home/y1weng/zebra_filter/calculate_coverages.py -i test/data/out2/aligned -o test/data/out2/coverages.tsv -d /home/y1weng/zebra_filter/databases/WoL/metadata.tsv"
        actual_commands = " ".join(
            _commands_generation_coverages(zebra_path, indir, outdir)
        )
        self.assertEqual(expected_commands, actual_commands)

    # module: index
    def test_cov_filter(self):
        # Use StringIO to simulate a file-like object
        cov_content = """
        gotu\tcoverage_ratio\ngenome1\t0.8\ngenome2\t0.6\ngenome3\t0.9\ngenome4\t0.5
        """
        cov_file = io.StringIO(cov_content.strip())
        cutoff_value = 0.7

        # Expected results
        expected_cov_filtered_content = """
        gotu\tcoverage_ratio\ngenome3\t0.9\ngenome1\t0.8
        """
        expected_cov_filtered = pd.read_csv(
            io.StringIO(expected_cov_filtered_content.strip()), sep="\t"
        )
        expected_gotu_filtered = pd.Series(["genome3", "genome1"], name="gotu")

        # Actual results
        actual_cov_filtered, actual_gotu_filtered = _cov_filter(cov_file, cutoff_value)

        # Reset indices before comparison
        expected_cov_filtered.reset_index(drop=True, inplace=True)
        actual_cov_filtered.reset_index(drop=True, inplace=True)
        expected_gotu_filtered.reset_index(drop=True, inplace=True)
        actual_gotu_filtered.reset_index(drop=True, inplace=True)

        # Comparison
        pd.testing.assert_frame_equal(expected_cov_filtered, actual_cov_filtered)
        pd.testing.assert_series_equal(expected_gotu_filtered, actual_gotu_filtered)

    def test_commands_generation_bt2build(self):
        output_fna_file = "/path/to/genomes.fna"
        output_bt2index = "/path/to/index"
        prefix = "my_index"
        threads = 64

        expected_commands = "bowtie2-build /path/to/genomes.fna /path/to/index/my_index --large-index -p 64"
        actual_commands = _commands_generation_bt2build(
            output_fna_file, output_bt2index, prefix, threads
        )

        # Assertions
        self.assertEqual(expected_commands, " ".join(actual_commands))

    # module: features
    def test_commands_generation_woltka(self):
        rank = "species"
        indir = "/path/to/indir"
        outdir = "/path/to/outdir"
        db = "/path/to/db"
        actual_commands = _commands_generation_woltka(rank, indir, outdir, db)
        expected_commands = [
            "woltka",
            "classify",
            "--input",
            "/path/to/indir",
            "--map",
            "/path/to/db/taxonomy/taxid.map",
            "--nodes",
            "/path/to/db/taxonomy/nodes.dmp",
            "--names",
            "/path/to/db/taxonomy/names.dmp",
            "--rank",
            "species",
            "--name-as-id",
            "--outmap",
            "/path/to/outdir/species_level/mapdir",
            "--output",
            "/path/to/outdir/species_level/counts_species.tsv",
        ]

        self.assertEqual(actual_commands, expected_commands)

    def test_commands_stratification_generation_woltka(self):
        rank = "species"
        indir = "/path/to/indir"
        outdir = "/path/to/outdir"
        db = "/path/to/db"
        commands = _commands_stratification_generation_woltka(rank, indir, outdir, db)
        expected_commands = [
            "woltka",
            "classify",
            "--input",
            "/path/to/indir",
            "--coords",
            "/path/to/db/proteins/coords.txt.xz",
            "--map",
            "/path/to/db/function/uniref/uniref.map.xz",
            "--map",
            "/path/to/db/function/go/process.map.xz",
            "--map-as-rank",
            "--rank",
            "process",
            "-n",
            "/path/to/db/function/uniref/uniref.name.xz",
            "-r",
            "uniref",
            "--stratify",
            "/path/to/outdir/species_level/mapdir",
            "--output",
            "/path/to/outdir/species_level/counts_species_stratified.tsv",
        ]
        self.assertEqual(commands, expected_commands)


if __name__ == "__main__":
    unittest.main()
