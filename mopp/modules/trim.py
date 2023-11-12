import shutil
import logging
import subprocess
from pathlib import Path
from mopp.modules.metadata import load_metadata

logger = logging.getLogger("mopp")


def trim_files(indir, outdir, md_path):
    # load metadata into md_dict
    md_dict = load_metadata(md_path)

    # create ./trimmed
    # if trimmed already exists in outdir, make sure it is empty
    outdir = Path(outdir) / "trimmed"
    outdir.mkdir(parents=True, exist_ok=True)

    for item in outdir.iterdir():
        if item.is_file():
            item.unlink()
        if item.is_dir():
            shutil.rmtree(item)

    # trim files
    for identifier, omic_dict in md_dict.items():
        for omic in omic_dict.keys():
            r1_file = Path(indir) / omic_dict[omic][0]
            if omic == "metaRS":
                logger.info(f"{r1_file.name} trimming started")
                _run_trim_metars(r1_file, outdir)
                _rename_files(outdir, identifier, omic)
            else:
                r2_file = Path(indir) / omic_dict[omic][1]
                logger.info(f"{r1_file.name} & R2 trimming started")
                _run_trim_paired(r1_file, r2_file, outdir)
                _cat_paired(outdir, identifier, omic)


def _rename_files(indir, identifier, omic):
    commands = [
        f"mv {indir}/{identifier}*{omic}*trimmed.fq.gz {indir}/{identifier}_{omic}_trimmed.fq.gz"
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
    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        logger.error(
            f"{r1_file.name} trimming failed with code {p.returncode} and error {error}"
        )
    else:
        logger.info(f"{r1_file.name} trimming finished")


def _cat_paired(indir, identifier, omic):
    commands = [
        f"cat {indir}/{identifier}*{omic}*.fq.gz > {indir}/{identifier}_{omic}_trimmed.fq.gz"
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
