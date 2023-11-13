import glob
import logging
import subprocess
from pathlib import Path
from mopp.modules.utils import clear_folder

logger = logging.getLogger("mopp")


def align_files(indir, outdir, INDEX, nthreads):
    outdir_aligned = Path(outdir) / "aligned"
    outdir_aligned.mkdir(parents=True, exist_ok=True)
    clear_folder(outdir_aligned)

    file_pattern = str(Path(indir) / "*.fq.gz")
    input_files = glob.glob(file_pattern)
    suffix = INDEX.split("/")[-1]

    for filepath in input_files:
        _run_align(filepath, suffix, outdir, INDEX, nthreads)


def _run_align(filepath, suffix, outdir, INDEX, nthreads):
    identifier = Path(filepath).name.split(".fq.gz")[0]
    commands = _commands_generation_bowtie2(
        filepath, identifier, suffix, outdir, INDEX, nthreads
    )
    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        err = (
            f"{identifier} alignment failed with code {p.returncode} and error {error}"
        )
        logger.error(err)
    else:
        logger.info(f"{identifier} alignment finished")


def _commands_generation_bowtie2(filepath, identifier, suffix, outdir, INDEX, nthreads):
    commands = [
        "bowtie2",
        "-U",
        filepath,
        "-x",
        INDEX,
        "-p",
        str(nthreads),
        "--no-unal",
        "--no-head",
        "-S",
        str(Path(outdir) / f"{identifier}_{suffix}.sam"),
        "2>",
        str(Path(outdir) / f"{identifier}_{suffix}.bow"),
    ]
    return commands


if __name__ == "__main__":
    align_files()
