import unittest
import pandas as pd
import numpy as np
import os
import subprocess
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from mopp.modules.coverages import plot_genome_density, plot_effect_of_filteration, calculate_coverages, sort_cov

class TestPlotGenomeDensity(unittest.TestCase):

    @patch('pandas.read_csv')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.fill_between')
    @patch('matplotlib.pyplot.ylim')
    @patch('matplotlib.pyplot.xlabel')
    @patch('matplotlib.pyplot.ylabel')
    @patch('matplotlib.pyplot.title')
    @patch('mopp.modules.coverages.gaussian_kde')
    def test_plot_genome_density(self, mock_kde, mock_title,
                                  mock_ylabel, mock_xlabel, mock_ylim, 
                                  mock_fill_between, mock_savefig, 
                                  mock_read_csv):

      
        mock_df = pd.DataFrame({
            'percent_covered': [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
        })
        mock_read_csv.return_value = mock_df

        mock_kde_instance = MagicMock()
        mock_kde.return_value = mock_kde_instance
        mock_kde_instance.evaluate.return_value = np.random.rand(10000)  

        plot_genome_density('test_input.tsv', 'output_directory')

        mock_read_csv.assert_called_once_with('test_input.tsv', sep="\t")
        mock_fill_between.assert_called()
        mock_savefig.assert_called_once_with('output_directory/density.png', dpi=300, bbox_inches='tight')

        mock_ylim.assert_called()

        mock_title.assert_called_once_with('Density Plot of Genome Coverage')
        mock_xlabel.assert_called_once_with('Genome Coverage (3-100%)')
        mock_ylabel.assert_called_once_with('Density')

        mock_kde.assert_called_once()
        mock_kde_instance.evaluate.assert_called()


class TestPlotEffectOfFiltration(unittest.TestCase):
    @patch('pandas.read_csv')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.xlabel')
    @patch('matplotlib.pyplot.ylabel')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.grid')
    def test_plot_effect_of_filteration(self, mock_grid, mock_title, mock_ylabel, 
                                         mock_xlabel, mock_plot, 
                                         mock_savefig, mock_read_csv):

        
        mock_df = pd.DataFrame({
            'percent_covered': [0, 5, 10, 15, 20, 25, 30]
        })
        mock_read_csv.return_value = mock_df

     
        plot_effect_of_filteration('test_input.tsv', 'output_directory')

       
        mock_read_csv.assert_called_once_with('test_input.tsv', sep="\t")
        mock_plot.assert_called()
        mock_savefig.assert_called_once_with('output_directory/feature_vs_coverage.png', dpi=300, bbox_inches='tight')

       
        mock_xlabel.assert_called_once_with('Minimum Coverage Percentage')
        mock_ylabel.assert_called_once_with('Number of OGUs remaining')
        mock_title.assert_called_once_with('Effect of Coverage Filtration on OGU count')
        mock_grid.assert_called_once()


class TestCalculateCoverages(unittest.TestCase):
    @patch('mopp.modules.coverages.subprocess.Popen')
    @patch('mopp.modules.coverages.glob')
    @patch('mopp.modules.coverages.create_folder_without_clear') 
    @patch('mopp.modules.coverages.plot_genome_density')  
    @patch('mopp.modules.coverages.plot_effect_of_filteration')
    @patch('mopp.modules.coverages.sort_cov')
    @patch('builtins.open', new_callable=mock_open) 
    def test_calculate_coverages_with_sam_xz_files(self, mock_file_open, mock_sort_cov, mock_plot_effect, mock_plot_genome_density, 
                                                    mock_create_folder, mock_glob, mock_popen):
        input_dir = 'test_input_dir'
        output_dir = 'test_output_dir'
        genome_lengths = 'genome_lengths.txt'

        mock_glob.return_value = ['file1.sam.xz', 'file2.sam.xz']

    
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = mock_process
        
       
        calculate_coverages(input_dir, output_dir, genome_lengths)

        mock_create_folder.assert_called_once_with(output_dir)
        mock_glob.assert_called_once_with(os.path.join(input_dir, "*.sam.xz"))


        expected_command = "xzcat file1.sam.xz file2.sam.xz | micov compress --output test_output_dir/coverage_calculation.tsv --lengths genome_lengths.txt"
        mock_popen.assert_called_once_with(expected_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        output_file = os.path.join(output_dir, "coverage_calculation.tsv")
        
       
        mock_plot_genome_density.assert_called_once()
        mock_plot_effect.assert_called_once()

    @patch('mopp.modules.coverages.subprocess.Popen')
    @patch('mopp.modules.coverages.glob')
    @patch('mopp.modules.coverages.create_folder_without_clear') 
    @patch('mopp.modules.coverages.plot_genome_density')  
    @patch('mopp.modules.coverages.plot_effect_of_filteration')
    @patch('mopp.modules.coverages.sort_cov')
    @patch('builtins.open', new_callable=mock_open)  
    def test_calculate_coverages_with_sam_files(self, mock_file_open, mock_sort_cov, mock_plot_effect, mock_plot_genome_density,
                                                 mock_create_folder, mock_glob, mock_popen):
        input_dir = 'test_input_dir'
        output_dir = 'test_output_dir'
        genome_lengths = 'genome_lengths.txt'

        
        mock_glob.side_effect = [
            [],  # First call: no .sam.xz files found
            ['file1.sam', 'file2.sam']  # Second call: .sam files found
        ]
        
     
        mock_join = MagicMock(side_effect=os.path.join)
   
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = mock_process

       
        calculate_coverages(input_dir, output_dir, genome_lengths)

        
        mock_create_folder.assert_called_once_with(output_dir)


        mock_glob.assert_any_call(mock_join(input_dir, "*.sam.xz"))
        mock_glob.assert_any_call(mock_join(input_dir, "*.sam"))

        
        expected_command = "cat file1.sam file2.sam | micov compress --output test_output_dir/coverage_calculation.tsv --lengths genome_lengths.txt"
        mock_popen.assert_called_once_with(expected_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        mock_plot_genome_density.assert_called_once()
        mock_plot_effect.assert_called_once()
   

    @patch('mopp.modules.coverages.glob')
    def test_calculate_coverages_no_files_found(self, mock_glob):
        mock_glob.return_value = []

        input_dir = 'test_input_dir'
        output_dir = 'test_output_dir'
        genome_lengths = 'genome_lengths.txt'

        with self.assertRaises(SystemExit):
            calculate_coverages(input_dir, output_dir, genome_lengths)

    def test_sort_cov(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        
        self.inpath = os.path.join(self.temp_dir.name, "input.tsv")
        self.outpath = os.path.join(self.temp_dir.name, "output.tsv")
        
        obs = {
            "genome_id": ["S1", "S2", "S3"],
            "covered": [15, 79, 32],
            "length": [10135, 6345, 15353],
            "percent_covered": [0.3, 0.2, 0.5],
        }
        df = pd.DataFrame(obs)
        df.to_csv(self.inpath, sep="\t", index=False)

        exp = {
            "genome_id": ["S3", "S1", "S2"],
            "covered": [32, 15, 79],
            "length": [15353, 10135, 6345],
            "percent_covered": [0.5, 0.3, 0.2],
        }
        df_exp = pd.DataFrame(exp)


        sort_cov(self.inpath, self.outpath)
        df_obs = pd.read_csv(self.outpath, sep="\t")
        

        pd.testing.assert_frame_equal(df_obs, df_exp)
        self.temp_dir.cleanup()
        

if __name__ == '__main__':
    unittest.main()
