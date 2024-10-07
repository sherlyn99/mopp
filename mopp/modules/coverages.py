import logging
import subprocess
import tempfile
from glob import glob
import os
from mopp.modules.utils import create_folder_without_clear


logger = logging.getLogger("mopp")


def calculate_coverages(input_dir, output_dir, genome_lengths):
    create_folder_without_clear(output_dir)

    with tempfile.TemporaryDirectory() as temp_dir:
        files_pattern = os.path.join(input_dir, '*.sam.*')
        files_to_decompress = glob(files_pattern)

        if files_to_decompress:
            subprocess.run(['7z', 'x', '*.sam.*', f'-o{temp_dir}'], cwd=input_dir, check=True)
            decompressed_files_pattern = os.path.join(temp_dir, '*.sam*')
        else:
            decompressed_files_pattern = os.path.join(input_dir, '*.sam*')

        
        decompressed_files = glob(decompressed_files_pattern)
        concatenated_file_path = os.path.join(temp_dir, 'concatenated.sam')

        if decompressed_files:
                files_list = ' '.join(decompressed_files)
                subprocess.run(f'cat {files_list} > {concatenated_file_path}', shell=True, check=True)


        commands = ['micov', 'compress', '--data', concatenated_file_path, '--output', output_dir, '--lengths', genome_lengths]
        p = subprocess.Popen(
            commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, error = p.communicate()
        if p.returncode != 0:
            err = f"Calculate coverages failed with code {p.returncode} and error {error.decode('utf-8')}"
            logger.error(err)
        else:
            logger.info(f"Calculate coverages finished")



if __name__ == "__main__":
    calculate_coverages()
