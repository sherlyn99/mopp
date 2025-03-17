import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import subprocess
from mopp.modules.features_wol import ft_generation, _commands_generation_woltka, _commands_stratification_generation_woltka


class TestFtGeneration(unittest.TestCase):
    @patch('mopp.modules.features_wol.create_folder_without_clear')
    @patch('mopp.modules.features_wol.subprocess.Popen')
    def test_ft_generation_genus(self, mock_popen, mock_create_folder):

        indir = 'test_input_dir'
        outdir = 'test_output_dir'
        db = 'test_db'
        rank = ['genus']
        stratification = True

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = mock_process

     
        with self.assertLogs('mopp', level='INFO') as logs:
            ft_generation(indir, outdir, db, rank, stratification)

        
        mock_create_folder.assert_called_once_with(Path(outdir))

        mock_popen.assert_any_call(
            _commands_generation_woltka("genus", indir, outdir, db),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        mock_popen.assert_any_call(
            _commands_stratification_generation_woltka("genus", indir, outdir, db),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )


    @patch('mopp.modules.features_wol.create_folder_without_clear')
    @patch('mopp.modules.features_wol.subprocess.Popen')
    def test_ft_generation_species(self, mock_popen, mock_create_folder):
  
        indir = 'test_input_dir'
        outdir = 'test_output_dir'
        db = 'test_db'
        rank = ['species']
        stratification = True

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = mock_process

        with self.assertLogs('mopp', level='INFO') as logs:
            ft_generation(indir, outdir, db, rank, stratification)

        mock_create_folder.assert_called_once_with(Path(outdir))

        
        mock_popen.assert_any_call(
            _commands_generation_woltka("species", indir, outdir, db),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        mock_popen.assert_any_call(
            _commands_stratification_generation_woltka("species", indir, outdir, db),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )


    def test_commands_generation_woltka(self):
    
        rank = "genus"
        indir = "test_input_dir"
        outdir = "test_output_dir"
        db = "test_db"

        commands = _commands_generation_woltka(rank, indir, outdir, db)

        expected_commands = [
            "woltka",
            "classify",
            "--input",
            indir,
            "--map",
            f"{db}/taxonomy/taxid.map",
            "--nodes",
            f"{db}/taxonomy/nodes.dmp",
            "--names",
            f"{db}/taxonomy/names.dmp",
            "--rank",
            rank,
            "--name-as-id",
            "--outmap",
            f"{outdir}/{rank}_level/mapdir",
            "--output",
            f"{outdir}/{rank}_level/counts_{rank}.tsv",
        ]

        self.assertEqual(commands, expected_commands)

    def test_commands_stratification_generation_woltka(self):

        rank = "genus"
        indir = "test_input_dir"
        outdir = "test_output_dir"
        db = "test_db"

    
        commands = _commands_stratification_generation_woltka(rank, indir, outdir, db)

        expected_commands = [
            "woltka",
            "classify",
            "--input",
            indir,
            "--coords",
            f"{db}/proteins/coords.txt.xz",
            "--map",
            f"{db}/function/uniref/orf-to-uniref.map.xz",
            "--rank",
            "uniref",
            "--names",
            f"{db}/function/uniref/uniref_name.txt.xz",
            "--stratify",
            f"{outdir}/{rank}_level/mapdir",
            "--output",
            f"{outdir}/{rank}_level/counts_{rank}_stratified.tsv",
        ]

        self.assertEqual(commands, expected_commands)


if __name__ == "__main__":
    unittest.main()
