import gzip
import lzma
import logging
import subprocess
import pandas as pd
from pathlib import Path
from mopp.modules.utils import create_folder_without_clear


logger = logging.getLogger("mopp")


def genome_extraction(
    cov: str, cutoff: float, refdb: str, outdir: str, prefix: str, nthreads: int
):
    """
    Only used for metagenomic data. Takes in a coverages.tsv, a cutoff, an outdir,
    and a prefix. Outputs:
    1) <outdir>/indexdb/<prefix>_filtered_genomes.fna: extracted genomes in .fna format,
    2) <outdir>/indexdb/<prefix>_filtered_bt2index: extracted genomes as a bowtie2 genome index,
    3) <outdir>/indexdb/<prefix>_filtered_coverages.tsv: iltered converage tsv,
    4) <outdir>/indexdb/<prefix>_filtered_gotu.txt: filtered genome ids.
    """
    # create output folder, erase if existed
    outdir_index = Path(outdir)
    create_folder_without_clear(outdir_index)

    cov_filtered, gotu_filtered = _cov_filter(cov, cutoff)
    gotu_filtered_list = _cov_filter_write(
        cov_filtered, gotu_filtered, outdir_index, prefix
    )

    output_bt2index = outdir_index / f"{prefix}_bt2index"
    create_folder_without_clear(output_bt2index)
    output_fna_file = _genome_extract(
        gotu_filtered_list, refdb, str(output_bt2index), prefix
    )
    _build_db(output_fna_file, output_bt2index, prefix, nthreads)


def _cov_filter(cov: str, cutoff: float):
    """
    Filter genomes based on coverage ratios.

    Parameters:
    - cov (str): Path to the coverage file in tab-separated format.
    - cutoff (float): The cutoff value for coverage ratios.

    Returns:
    A tuple containing two pandas objects:
    - cov_filtered (pd.DataFrame): Filtered table of coverage information.
    - gotu_filtered (pd.Series): Filtered genome IDs.
    """
    cov = pd.read_csv(cov, sep="\t")
    cov_filtered = cov.loc[cov["percent_covered"] >= cutoff]
    cov_filtered = cov_filtered.sort_values(by="percent_covered", ascending=False)
    gotu_filtered = cov_filtered["genome_id"]
    return cov_filtered, gotu_filtered


def _cov_filter_write(
    cov_filtered: pd.DataFrame, gotu_filtered: pd.DataFrame, outdir: str, prefix: str
):
    """
    Generate files based on filtered genome information.

    Parameters:
    - cov_filtered (pd.DataFrame): Filtered table of coverage information.
    - gotu_filtered (pd.Series): Filtered genome IDs.
    - outdir (str): The output directory path.
    - prefix (str): A prefix for the generated files.

    Returns:
    A list containing the filtered genome IDs.
    """
    # write .tsv and .txt files
    cov_filtered.to_csv(
        Path(outdir) / f"{prefix}_filtered_coverages.tsv",
        index=False,
        header=True,
        sep="\t",
    )
    logger.info(f"{prefix}_filtered_coverages.tsv created")
    gotu_filtered.to_csv(
        Path(outdir) / f"{prefix}_filtered_gotu.txt", index=False, header=False
    )
    logger.info(f"{prefix}_filtered_gotu.txt created")
    return gotu_filtered.to_list()


def _genome_extract(genome_ids: list, ref_db: str, outdir: str, prefix: str):
    """
    Extract genomes from a reference database based on a list of genome IDs.

    Parameters:
    - genome_ids (List[str]): A list of genome IDs to extract.
    - ref_db (str): Path to the reference database file (.fna, .fna.gz, .fna.xz).
    - outdir (str): Output directory path.
    - prefix (str): Prefix for the generated files.

    Returns:
    A string representing the path to the generated .fna file containing filtered genomes.

    Raises:
    - IOError: If the file extension of the reference database is unrecognized.
    """
    # load ref db
    open_fna_file = None
    if ref_db.endswith(".fna"):
        open_fna_file = open(ref_db.strip(), "r")
    elif ref_db.endswith(".fna.gz"):
        open_fna_file = gzip.open(ref_db.strip(), mode="rt", encoding="utf-8")
    elif ref_db.endswith(".fna.xz"):
        open_fna_file = lzma.open(ref_db.strip(), mode="rt", encoding="utf-8")
    else:
        raise IOError(f"Unrecognized file extension on {ref_db}.")

    # turn list of genome ids into set
    genome_ids = set(genome_ids)

    # search for filtered genome IDs and writes out .fna file
    output_fna_file = outdir + f"/{prefix}_filtered_genomes.fna"
    with open_fna_file as in_fna, open(output_fna_file, "w") as out_fna:
        capture = False
        for line in in_fna:
            line = line.strip()
            if line.startswith(">") and line[1:] in genome_ids:
                out_fna.write(line + "\n")
                capture = True
            elif capture:
                out_fna.write(line + "\n")
                capture = False
    logger.info(f"{output_fna_file} created")
    return output_fna_file


def _build_db(output_fna_file: str, outdir: str, prefix: str, nthreads: int):
    """
    Build a Bowtie2 index from a filtered genome FASTA file.

    Parameters:
    - output_fna_file (str): Path to the filtered genome FASTA file.
    - outdir (str): Output directory path for the Bowtie2 index.
    - prefix (str): Prefix for the Bowtie2 index files.

    Returns:
    A string representing the path to the created Bowtie2 index.

    Notes:
    The function creates a directory for the Bowtie2 index in the specified output directory.
    The Bowtie2 index files will have the specified prefix.
    """
    # create directory for bt2 index
    output_bt2index = outdir
    # create_folder(output_bt2index)

    commands = _commands_generation_bt2build(
        output_fna_file, output_bt2index, prefix, nthreads
    )
    logger.info(f"{prefix} indexdb creation started")
    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        err = f"{prefix} indexdb failed with code {p.returncode} and error {error.decode('utf-8')}"
        logger.error(err)
    else:
        logger.info(f"{prefix} indexdb created")


def _commands_generation_bt2build(
    output_fna_file: str, output_bt2index: Path, prefix: str, nthreads: int
):
    commands = [
        "bowtie2-build",
        output_fna_file,
        f"{output_bt2index}/{prefix}",
        "--large-index",
        # "-p",
        # str(nthreads),
    ]
    return commands


if __name__ == "__main__":
    genome_extraction()
