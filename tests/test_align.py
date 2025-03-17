import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from mopp.modules.align import align_files, _run_align, _commands_generation_bowtie2


class TestAlignment(unittest.TestCase):
    @patch('mopp.modules.align.glob.glob')
    @patch('mopp.modules.align.create_folder_without_clear')
    @patch('mopp.modules.align.subprocess.Popen')
    @patch('mopp.modules.align.lzma.open', new_callable=mock_open)
    @patch('builtins.open', new_callable=mock_open)
    @patch('mopp.modules.align.Path.unlink')
    def test_align_files(self, mock_unlink, mock_file_open, mock_lzma_open, mock_popen, mock_create_folder, mock_glob):
        indir = 'test_input_dir'
        outdir = 'test_output_dir'
        pattern = '*.fq.gz'
        INDEX = 'test_index'
        nthreads = 4
        compress = True

        mock_glob.return_value = ['file1.fq.gz', 'file2.fq.gz']

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = mock_process

    
        align_files(indir, outdir, pattern, INDEX, nthreads, compress)

        mock_create_folder.assert_any_call(Path(outdir))
        mock_create_folder.assert_any_call(Path(outdir) / "samfiles")
        mock_create_folder.assert_any_call(Path(outdir) / "bowfiles")

        mock_glob.assert_called_once_with(str(Path(indir) / pattern))

        self.assertEqual(mock_popen.call_count, 2) 
        self.assertEqual(mock_lzma_open.call_count, 2)  

    @patch('mopp.modules.align.subprocess.Popen')
    @patch('mopp.modules.align.lzma.open', new_callable=mock_open)
    @patch('builtins.open', new_callable=mock_open)
    @patch('mopp.modules.align.Path.unlink')  
    def test_run_align(self, mock_unlink, mock_file_open, mock_lzma_open, mock_popen):
       
        filepath = 'file1.fq.gz'
        suffix = 'test_index_suffix'
        outdir = 'test_output_dir'
        INDEX = 'test_index'
        nthreads = 4
        compress = True

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = mock_process

        mock_file = MagicMock()
        mock_file_open.return_value = mock_file
        mock_lzma_file = MagicMock()
        mock_lzma_open.return_value = mock_lzma_file

        
        _run_align(filepath, suffix, outdir, INDEX, nthreads, compress)

        mock_popen.assert_called_once()
        mock_lzma_open.assert_called_once()
        mock_unlink.assert_called_once_with()

    def test_commands_generation_bowtie2(self):
      
        filepath = 'file1.fq.gz'
        identifier = 'file1'
        suffix = 'test_index_suffix'
        outdir = 'test_output_dir'
        INDEX = 'test_index'
        nthreads = 4

        commands = _commands_generation_bowtie2(filepath, identifier, suffix, outdir, INDEX, nthreads)

        expected_commands = [
            "bowtie2",
            "-U", filepath,
            "-x", INDEX,
            "-p", str(nthreads),
            "--no-unal",
            "--no-head",
            "-S", str(Path(outdir) / "samfiles" / f"{identifier}_{suffix}.sam"),
            "2>", str(Path(outdir) / "bowfiles" / f"{identifier}_{suffix}.bow"),
        ]

       
        self.assertEqual(commands, expected_commands)

    @patch('mopp.modules.align.glob.glob')
    def test_align_files_no_files_found(self, mock_glob):

        indir = 'test_input_dir'
        outdir = 'test_output_dir'
        pattern = '*.fq.gz'
        INDEX = 'test_index'
        nthreads = 4
        compress = True

        
        mock_glob.return_value = []
        
        with self.assertRaises(FileNotFoundError):
            align_files(indir, outdir, pattern, INDEX, nthreads, compress)

        mock_glob.assert_called_once_with(str(Path(indir) / pattern))


if __name__ == "__main__":
    unittest.main()
