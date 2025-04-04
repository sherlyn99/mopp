import sys
import shutil
import logging
import subprocess
from pathlib import Path
from mopp.modules.utils import pool_processes
from mopp.modules.utils import create_folder_without_clear
from mopp.modules.metadata import load_metadata_to_dict_with_validation


logger = logging.getLogger("mopp")

def run_trim_metars(args):
    r1, outdir = args
    return _run_trim_metars(r1, outdir)


def run_trim_paired(args):
    r1, r2, outdir = args
    return _run_trim_paired(r1, r2, outdir)


def rename_files(args):
    outdir_trimmed, outdir_cat, identifier, omic, stem = args
    return _rename_files(outdir_trimmed, outdir_cat, identifier, omic, stem)


def cat_paired(args):
    outdir_trimmed, outdir_cat, identifier, omic, stem = args
    return _cat_paired(outdir_trimmed, outdir_cat, identifier, omic, stem)


def trim_files(indir, outdir, md_path, threads):
    # check if trim_galore is installed
    if shutil.which("trim_galore") is None:
        logger.error("trim_galore is not installed or not found in the system path.")
        sys.exit(1)
        return  # Exit the function if trim_galore is not available

    # load metadata into md_dict
    md_dict = load_metadata_to_dict_with_validation(md_path)

    # create ./trimmed, if outdir already existed, will not clear content, might overwrite
    outdir_cat = Path(outdir)
    outdir_trimmed = Path(outdir_cat) / "trimmed_reports"
    create_folder_without_clear(outdir_cat)
    create_folder_without_clear(outdir_trimmed)

    arg_list_metars = []
    arg_list_trimpaired = []
    arg_list_renamefiles = []
    arg_list_catpaired = []

    for identifier, omic_dict in md_dict.items():
        for omic in omic_dict.keys():
            r1_file = Path(indir) / omic_dict[omic][0]
            r1_stem = str.split(str(r1_file.name), ".")[0]

            if len(omic_dict[omic]) == 2:
                r2_file = Path(indir) / omic_dict[omic][1]
                r2_stem = str.split(str(r2_file.name), ".")[0]
                arg_list_trimpaired.append((r1_file, r2_file, outdir_trimmed))
                arg_list_catpaired.append(
                    (outdir_trimmed, outdir_cat, identifier, omic, r2_stem)
                )
            else:
                arg_list_metars.append((r1_file, outdir_trimmed))
                arg_list_renamefiles.append(
                    (outdir_trimmed, outdir_cat, identifier, omic, r1_stem)
                )

    pool_processes(
        threads,
        [
            [run_trim_metars, arg_list_metars],
            [run_trim_paired, arg_list_trimpaired],
        ],
    )
    pool_processes(
        threads,
        [
            [rename_files, arg_list_renamefiles],
            [cat_paired, arg_list_catpaired],
        ],
    )


def _rename_files(indir, outdir, identifier, omic, stem):
    commands = [
        f"mv {indir}/{stem}*trimmed.fq.gz {outdir}/{identifier}_{omic}_trimmed.fq.gz"
    ]
    p = subprocess.Popen(
        commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = p.communicate()
    if p.returncode != 0:
        err = f"Renaming {stem} trimmed files failed with code {p.returncode} and error {error.decode('utf-8')}"
        logger.error(err)
    else:
        logger.info(f"Renaming {stem} trimmed files finished")


def _run_trim_paired(r1_file, r2_file, outdir):
    if shutil.which("trim_galore") is None:
        logger.error("trim_galore is not installed or not found in the system path.")
        return  
    
    commands = [
        "trim_galore",
        "--paired",
        r1_file,
        r2_file,
        "--output_dir",
        outdir,
        "--length",
        "20",
        "--fastqc",
    ]
    logger.info(f"{r1_file.name} & R2 trimming started")
    p = subprocess.Popen(
        commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = p.communicate()
    if p.returncode != 0:
        err = f"{r1_file.name} & R2 trimming failed with code {p.returncode} and error {error.decode('utf-8')}"
        logger.error(err)
    else:
        logger.info(f"{r1_file.name} & R2 trimming finished")


def _run_trim_metars(r1_file, outdir):
    commands = [
        "trim_galore",
        r1_file,
        "--output_dir",
        outdir,
        "--length",
        "18",
        "--max_length",
        "75",
        "--fastqc",
    ]
    logger.info(f"{r1_file.name} trimming started")
    p = subprocess.Popen(
        commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = p.communicate()
    if p.returncode != 0:
        logger.error(
            f"{r1_file.name} trimming failed with code {p.returncode} and error {error.decode('utf-8')}"
        )
    else:
        logger.info(f"{r1_file.name} trimming finished")


def _cat_paired(indir, outdir, identifier, omic, stem):
    stem = stem.split("R2")[0]
    commands = [
        f"cat {indir}/{stem}*.fq.gz > {outdir}/{identifier}_{omic}_trimmed.fq.gz"
    ]
    p = subprocess.Popen(
        commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = p.communicate()
    if p.returncode != 0:
        err = f"Concatenation of {stem.rstrip('_')} trimmed files failed with code {p.returncode} and error {error}"
        logger.error(err)
    else:
        logger.info(
            f"Concatenation of {stem.rstrip('_')} trimmed files finished"
        )
    return


if __name__ == "__main__":
    trim_files()
