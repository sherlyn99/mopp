import click
import os
import subprocess
import pathlib

from mopp._defaults import (DESC_MD, DESC_INPUT, DESC_OUTPUT)

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

def align_files(indir, outdir, md_dict, INDEX):
    outdir = os.path.join(outdir, 'aligned')
    os.makedirs(outdir, exist_ok=True)

    for identifer, omic_info_dict in md_dict.items():
        for omic, files in omic_info_dict.items():
            r1_file = os.path.join(indir, omic_info_dict[omic][0])
            if omic == 'metars':
                print(f'{r1_file} detected')
                _run_align_metars(r1_file, outdir, INDEX)
            else:
                r2_file = os.path.join(indir, omic_info_dict[omic][1])
                print(f'{r1_file} and {r2_file} detected')
                _run_align_paired(r1_file, r2_file, outdir, INDEX)


def _run_align_paired(r1_file, r2_file, outdir, INDEX):
    commands = [
        'bowtie2',
        '-1', r1_file, 
        '-2', r2_file,
        '-x', INDEX,
        '-p', '8',
        '--no-unal',
        '--no-head',
        '-S', os.path.join(outdir, r1_file.split("/")[-1] + "_WoL_subset.sam"),
        '2>', os.path.join(outdir, r1_file.split("/")[-1] + "_WoL_subset.bow")
    ]

    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        logging.error(f'{os.path.basename(r1_file)} & R2 aligning failed with code {p.returncode} and error {error}')
    else:
        logging.info(f'{os.path.basename(r1_file)} & R2 aligning finished')

def _run_align_metars(r1_file, outdir, INDEX):
    commands = [
        'bowtie2',
        '-U', r1_file,
        '-x', INDEX,
        '-p', '8', 
        '--no-unal',
        '--no-head',
        '-S', os.path.join(outdir, r1_file.split("/")[-1] + "_WoL_subset.sam"),
        '2>', os.path.join(outdir, r1_file.split("/")[-1] + "_WoL_subset.bow")
    ]

    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        logging.error(f'{os.path.basename(r1_file)} aligning failed with code {p.returncode} and error {error}')
    else:
        logging.info(f'{os.path.basename(r1_file)} aligning finished')

