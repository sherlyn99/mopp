import click
import os
import subprocess
import pathlib

from mopp._defaults import (DESC_MD, DESC_INPUT, DESC_OUTPUT)
from mopp.modules import load_metadata, md_to_dict

import logging
import time
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(
    filename=f'trim_{timestamp}.log',
    level=logging.DEBUG, 
    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')

# test run (from project root): python ./mopp/modules/trim.py
# todos: 
# 1. auto concatenate metag and metat trimmed reads
# 2. delete unnecessary files such as *fastqc.zip
# 3. following up on 2, should we delete trim_val1 and trim_val2 and fastqc report?
# 4. consider reorganization of code so that metag, metat, and metars can be run separately

def trim_files(indir, outdir, md_dict):
    outdir = os.path.join(outdir, 'trimmed')
    os.makedirs(outdir, exist_ok=True)

    for identifer, omic_info_dict in md_dict.items():
        for omic, files in omic_info_dict.items():
            r1_file = os.path.join(indir, omic_info_dict[omic][0])
            if omic == 'metaRS':
                print(f'{r1_file} detected')
                _run_trim_metars(r1_file, outdir)

            else:
                r2_file = os.path.join(indir, omic_info_dict[omic][1])
                print(f'{r1_file} and {r2_file} detected')
                _run_trim_paired(r1_file, r2_file, outdir)
    _concat_paired(outdir,md_dict)

def _run_trim_paired(r1_file, r2_file, outdir):
    commands = [
        'trim_galore',
        '--paired', r1_file, r2_file,
        '--output_dir', outdir,
        '--length', '20',
        '--fastqc'
    ]
    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        logging.error(f'{os.path.basename(r1_file)} & R2 trimming failed with code {p.returncode} and error {error}')
    else:
        logging.info(f'{os.path.basename(r1_file)} & R2 trimming finished')

def _run_trim_metars(r1_file, outdir):
    commands = [
        'trim_galore', r1_file,
        '--output_dir', outdir,
        '--length', '18',
        '--max_length', '75', 
        '--fastqc'
    ]
    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        logging.error(f'{os.path.basename(r1_file)} trimming failed with code {p.returncode} and error {error}')
    else:
        logging.info(f'{os.path.basename(r1_file)} trimming finished')

def _concat_paired(dir, md_dict):

    for identifer, omic_info_dict in md_dict.items():
        for omic, files in omic_info_dict.items():

            commands = [
                f"cat {dir}/{identifer}*metaG*.fq.gz >{dir}/{identifer}_metaG_cat_trimmed.fq.gz"
            ]
    
    p = subprocess.Popen(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    print(output, error)


if __name__ == '__main__':
    trim_files("./test/data/", './test/out',  md_to_dict(load_metadata('./test/data/metadata.tsv')))
    #_concat_paired('./test/out/trimmed', md_to_dict(load_metadata('./test/data/metadata.tsv')))

