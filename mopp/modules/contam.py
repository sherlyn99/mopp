import subprocess
import logging
from pathlib import Path
from mopp.modules.utils import pool_processes
from mopp.modules.utils import create_folder_without_clear
from mopp.modules.metadata import load_metadata_to_dict_with_validation
import os

logger = logging.getLogger("mopp")


def calculate_contamination(indir, outdir, md_path, threads):
  
   md_dict = load_metadata_to_dict_with_validation(md_path)

   outdir_contam = os.path.join(outdir, "contam")

   for identifier, omic_dict in md_dict.items():
       for omic in omic_dict.keys():
           r1_file = Path(indir) / omic_dict[omic][0]

           if len(omic_dict[omic]) == 2:
               r2_file = Path(indir) / omic_dict[omic][1]
               _run_contam_check_paired(r1_file, r2_file, os.path.join(outdir_contam, r1_file.name), threads)
           else:
               _run_contam_check_metars(r1_file, os.path.join(outdir_contam, r1_file.name), threads)


def _run_contam_check_metars(r1, outdir, threads):
   commands = [
    "sortmerna",
    "--ref", "mopp/refdb/gtrnadb-search201735_fixed.fasta",
    "--ref", "mopp/refdb/smr_v4.3_fast_db.fasta",
    "--reads", r1,
    "--workdir", outdir,
    "--fastx", " ",
    "--sam", " ",
    "--other", os.path.join(outdir, "out/clean"),
    "--blast", "1 cigar qcov qstrand",
    "--threads", str(threads)
]
   logger.info(f"{r1.name} alignment to tRNA and rRNA started")
   p = subprocess.Popen(
       commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE
   )
   output, error = p.communicate()

   
   if p.returncode != 0:
       err = f"{r1.name} alignment to tRNA and rRNA failed with code {p.returncode} and error {error.decode('utf-8')}"
       logger.error(err)
   else:
       logger.info(f"{r1.name} alignment to tRNA and rRNA finished")


def _run_contam_check_paired(r1, r2, outdir, threads): 
    commands = [
    "sortmerna",
    "--ref", "mopp/refdb/gtrnadb-search201735_fixed.fasta",
    "--ref", "mopp/refdb/smr_v4.3_fast_db.fasta",
    "--reads", r1,
    "--reads", r2,
    "--workdir", outdir,
    "--fastx", " ",
    "--sam", " ",
    "--other", os.path.join(outdir, "out/clean"),
    "--blast", "1 cigar qcov qstrand",
    "--threads", str(threads)
]
    print(commands)
    logger.info(f"{r1.name} & R2 alignment to tRNA and rRNA started")
    p = subprocess.Popen(
       commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE
   )
    
    output, error = p.communicate()
    if p.returncode != 0:
       err = f"{r1.name} & R2 alignment to tRNA and rRNA failed with code {p.returncode} and error {error.decode('utf-8')}"
       logger.error(err)
    else:
       logger.info(f"{r1.name} & R2 alignment to tRNA and rRNA finished")
