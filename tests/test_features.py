import unittest
from mopp.modules.features import (
    gen_commands_features,
    gen_commands_collapse,
    run_command,
)


class FeaturesTests(unittest.TestCase):
    def test_gen_commands_features_1(self):
        # ogu.tsv
        obs = gen_commands_features(
            "./tests/test_run/mopp_out/aligned/samfiles",
            "./tests/test_run/mopp_out/features/ogu.tsv",
            "./tests/test_run/mopp_out/features/mapdir",
            None,
        )
        obs_string = " ".join(obs)
        exp_string = "woltka classify -i ./tests/test_run/mopp_out/aligned/samfiles -o ./tests/test_run/mopp_out/features/ogu.tsv --outmap ./tests/test_run/mopp_out/features/mapdir"
        self.assertEqual(obs_string, exp_string)

    def test_gen_commands_features_2(self):
        # ogu_orf.tsv
        obs = gen_commands_features(
            "./tests/test_run/mopp_out/aligned/samfiles",
            "./tests/test_run/mopp_out/features/ogu_orf.tsv",
            "./tests/test_run/mopp_out/features/mapdir",
            "/projects/wol/qiyun/wol2/proteins/coords.txt.xz",
        )
        obs_string = " ".join(obs)
        exp_string = "woltka classify -i ./tests/test_run/mopp_out/aligned/samfiles -o ./tests/test_run/mopp_out/features/ogu_orf.tsv --coords /projects/wol/qiyun/wol2/proteins/coords.txt.xz --stratify ./tests/test_run/mopp_out/features/mapdir"
        self.assertEqual(obs_string, exp_string)

    def test_gen_commands_collapse_1(self):
        # tax.tsv
        obs = gen_commands_collapse(
            "./tests/test_run/mopp_out/features/ogu.tsv",
            "./tests/test_run/mopp_out/features/tax.tsv",
            None,
            None,
            "/projects/wol/qiyun/wol2/taxonomy/taxid.map",
            None,
            None,
        )
        obs_string = " ".join(obs)
        exp_string = "woltka collapse -i ./tests/test_run/mopp_out/features/ogu.tsv -o ./tests/test_run/mopp_out/features/tax.tsv -m /projects/wol/qiyun/wol2/taxonomy/taxid.map"
        self.assertEqual(obs_string, exp_string)

    def test_gen_commands_collapse_2(self):
        # tax_orf.tsv
        obs = gen_commands_collapse(
            "./tests/test_run/mopp_out/features/ogu_orf.tsv",
            "./tests/test_run/mopp_out/features/tax_orf.tsv",
            "|",
            1,
            "/projects/wol/qiyun/wol2/taxonomy/taxid.map",
            None,
            None,
        )
        obs_string = " ".join(obs)
        exp_string = "woltka collapse -i ./tests/test_run/mopp_out/features/ogu_orf.tsv -o ./tests/test_run/mopp_out/features/tax_orf.tsv -m /projects/wol/qiyun/wol2/taxonomy/taxid.map -s | -f 1"
        self.assertEqual(obs_string, exp_string)

    def test_gen_commands_collapse_3(self):
        # tax_func.tsv
        obs = gen_commands_collapse(
            "./tests/test_run/mopp_out/features/tax_orf.tsv",
            "./tests/test_run/mopp_out/features/tax_func.tsv",
            "|",
            2,
            "/projects/wol/qiyun/wol2/function/uniref/orf-to-uniref.map.xz",
            None,
            None,
        )
        obs_string = " ".join(obs)
        exp_string = "woltka collapse -i ./tests/test_run/mopp_out/features/tax_orf.tsv -o ./tests/test_run/mopp_out/features/tax_func.tsv -m /projects/wol/qiyun/wol2/function/uniref/orf-to-uniref.map.xz -s | -f 2"
        self.assertEqual(obs_string, exp_string)

    def test_gen_commands_collapse_4(self):
        # ogu_func.tsv
        obs = gen_commands_collapse(
            "./tests/test_run/mopp_out/features/ogu_orf.tsv",
            "./tests/test_run/mopp_out/features/ogu_func.tsv",
            "|",
            2,
            "/projects/wol/qiyun/wol2/function/uniref/orf-to-uniref.map.xz",
            None,
            None,
        )
        obs_string = " ".join(obs)
        exp_string = "woltka collapse -i ./tests/test_run/mopp_out/features/ogu_orf.tsv -o ./tests/test_run/mopp_out/features/ogu_func.tsv -m /projects/wol/qiyun/wol2/function/uniref/orf-to-uniref.map.xz -s | -f 2"
        self.assertEqual(obs_string, exp_string)

    def test_run_command_success(self):
       
        with self.assertLogs(logger="mopp", level="INFO") as logs:
            run_command(["echo", "Hello, World!"], "Test command")

        
        self.assertIn("Test command started", logs.output[0])
        self.assertIn("Test command finished", logs.output[1])


if __name__ == "__main__":
    unittest.main()
