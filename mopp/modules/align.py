import glob
import lzma
import logging
import subprocess
from pathlib import Path
from mopp.modules.utils import create_folder, create_folder_without_clear


logger = logging.getLogger("mopp")


def align_files(indir, outdir, pattern, INDEX, nthreads, compress=True):
    outdir_aligned = Path(outdir)
    create_folder_without_clear(outdir_aligned)

    outdir_aligned_samfiles = outdir_aligned / "samfiles"
    outdir_aligned_bowfiles = outdir_aligned / "bowfiles"
    create_folder_without_clear(outdir_aligned_samfiles)
    create_folder_without_clear(outdir_aligned_bowfiles)

    file_pattern = str(Path(indir) / pattern)
    input_files = glob.glob(file_pattern)
    if len(input_files) == 0:
        raise FileNotFoundError(file_pattern)
    suffix = INDEX.split("/")[-1]

    for filepath in input_files:
        _run_align(filepath, suffix, outdir_aligned, INDEX, nthreads, compress)


def _run_align(filepath, suffix, outdir, INDEX, nthreads, compress=True):
    identifier = Path(filepath).name.split(".fq.gz")[0]
    commands = _commands_generation_bowtie2(
        filepath, identifier, suffix, outdir, INDEX, nthreads
    )
    logger.info(f"{Path(filepath).name} alignment started")
    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        err = f"{Path(filepath).name} alignment failed with code {p.returncode} and error {error.decode('utf-8')}"
        logger.error(err)
    else:
        logger.info(f"{Path(filepath).name} alignment finished")

    if compress:
        file_to_compress = Path(outdir) / "samfiles" / f"{identifier}_{suffix}.sam"
        file_compressed = Path(outdir) / "samfiles" / f"{identifier}_{suffix}.sam.xz"

        with open(file_to_compress, "rb") as input_file, lzma.open(
            file_compressed, "wb"
        ) as output_file:
            output_file.writelines(input_file)
        file_to_compress.unlink()
        logger.info(f"{Path(filepath).name} samfile zipped.")


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
        str(Path(outdir) / "samfiles" / f"{identifier}_{suffix}.sam"),
        "2>",
        str(Path(outdir) / "bowfiles" / f"{identifier}_{suffix}.bow"),
    ]
    return commands


if __name__ == "__main__":
    align_files()
