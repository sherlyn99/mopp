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
    for file in os.listdir(indir):
        _run_align(file, outdir, INDEX)


def _run_align(file, outdir, INDEX):
    newname = file.split("/")[-1]

    if "_trimmed" in file:
        newname = newname.split("_trimmed")[0]
    elif "_concat" in file:
        newname = newname.split("_concat")[0]

    commands = [
        'bowtie2',
        '-U', file,
        '-x', INDEX,
        '-p', '8', 
        '--no-unal',
        '--no-head',
        '-S', os.path.join(outdir, newname + "_WoL_subset.sam"),
        '2>', os.path.join(outdir, newname + "_WoL_subset.bow")
    ]
    

    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        logging.error(f'{os.path.basename(file)} aligning failed with code {p.returncode} and error {error}')
    else:
        logging.info(f'{os.path.basename(file)} aligning finished')


if __name__ == '__main__':
    _run_align_paired("./test/data/out_manual/trimmed/1-1_t2_metaT_S37_L004_R1_001.250k_val_1.fq.gz", './test/data/out_manual/trimmed/1-1_t2_metaT_S37_L004_R2_001.250k_val_2.fq.gz',  './test/out', '/home/kz/Pictures/ecoli_index')

