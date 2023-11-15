import logging
import subprocess
from pathlib import Path
from mopp.modules.utils import create_folder
from mopp.modules.metadata import load_metadata


logger = logging.getLogger("mopp")


def trim_files(indir, outdir, md_path):
    # load metadata into md_dict
    md_dict = load_metadata(md_path)

    # create ./trimmed
    # if outdir already existed, will clear content
    outdir_cat = Path(outdir)
    outdir_trimmed = Path(outdir_cat) / "trimmed_reports"
    create_folder(outdir_cat)
    create_folder(outdir_trimmed)

    # trim files
    for identifier, omic_dict in md_dict.items():
        for omic in omic_dict.keys():
            r1_file = Path(indir) / omic_dict[omic][0]
            if omic == "metaRS":
                _run_trim_metars(r1_file, outdir_trimmed)
                _rename_files(outdir_trimmed, outdir_cat, identifier, omic)
            else:
                r2_file = Path(indir) / omic_dict[omic][1]

                _run_trim_paired(r1_file, r2_file, outdir_trimmed)
                _cat_paired(outdir_trimmed, outdir_cat, identifier, omic)


def _rename_files(indir, outdir, identifier, omic):
    commands = [
        f"mv {indir}/{identifier}*{omic}*trimmed.fq.gz {outdir}/{identifier}_{omic}_trimmed.fq.gz"
    ]
    p = subprocess.Popen(
        commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = p.communicate()
    if p.returncode != 0:
        err = f"Renaming {identifier}_{omic} trimmed files failed with code {p.returncode} and error {error}"
        logger.error(err)
    else:
        logger.info(f"Renaming {identifier}_{omic} trimmed files finished")


def _run_trim_paired(r1_file, r2_file, outdir):
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
    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        err = f"{r1_file.name} & R2 trimming failed with code {p.returncode} and error {error}"
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
    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        logger.error(
            f"{r1_file.name} trimming failed with code {p.returncode} and error {error}"
        )
    else:
        logger.info(f"{r1_file.name} trimming finished")


def _cat_paired(indir, outdir, identifier, omic):
    commands = [
        f"cat {indir}/{identifier}*{omic}*.fq.gz > {outdir}/{identifier}_{omic}_trimmed.fq.gz"
    ]
    p = subprocess.Popen(
        commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = p.communicate()
    if p.returncode != 0:
        err = f"Concatenation of {identifier}_{omic} trimmed files failed with code {p.returncode} and error {error}"
        logger.error(err)
    else:
        logger.info(f"Concatenation of {identifier}_{omic} trimmed files finished")
    return


if __name__ == "__main__":
    trim_files()
