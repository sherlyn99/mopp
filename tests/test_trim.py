import unittest
import shutil
import logging
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from mopp.modules.trim import (
    run_trim_metars,
    run_trim_paired,
    rename_files,
    cat_paired,
    trim_files,
    _rename_files,
    _run_trim_paired,
    _run_trim_metars,
    _cat_paired
)

class trimTests(unittest.TestCase):
    def setUp(self):
        self.outdir = "test_outdir"
        self.indir = "test_indir"
        self.md_path = "test_metadata.csv"
        self.threads = 4

    def tearDown(self):
        pass

    @patch("mopp.modules.trim.shutil.which", return_value=None)
    def test_trim_files_no_trim_galore(self, mock_shutil):
        with self.assertRaises(SystemExit):
            trim_files(self.indir, self.outdir, self.md_path, self.threads)
    
    @patch("mopp.modules.trim.subprocess.Popen")
    def test_run_trim_paired_success(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"output", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        r1_file = Path("sample_R1.fq.gz")
        r2_file = Path("sample_R2.fq.gz")
        outdir = Path("output")
        
        _run_trim_paired(r1_file, r2_file, outdir)
        mock_popen.assert_called()

    @patch("mopp.modules.trim.subprocess.Popen")
    def test_run_trim_paired_failure(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"", b"Error message")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        r1_file = Path("sample_R1.fq.gz")
        r2_file = Path("sample_R2.fq.gz")
        outdir = Path("output")
        
        with self.assertLogs(level=logging.ERROR) as log:
            _run_trim_paired(r1_file, r2_file, outdir)
        self.assertIn("trimming failed", log.output[0])

    @patch("mopp.modules.trim.subprocess.Popen")
    def test_rename_files_success(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"output", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        _rename_files("input_dir", "output_dir", "id1", "metaG", "sample1")
        mock_popen.assert_called()
    
    @patch("mopp.modules.trim.subprocess.Popen")
    def test_cat_paired_success(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"output", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        _cat_paired("indir", "outdir", "sample1", "metaG", "sample1_R2")
        mock_popen.assert_called()
    
    @patch("mopp.modules.trim.subprocess.Popen")
    def test_cat_paired_failure(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"", b"Error message")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        with self.assertLogs(level=logging.ERROR) as log:
            _cat_paired("indir", "outdir", "sample1", "metaG", "sample1_R2")
        self.assertIn("Concatenation", log.output[0])

if __name__ == "__main__":
    unittest.main()
