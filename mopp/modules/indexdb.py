import gzip
import lzma
from pathlib import Path
import pandas as pd
import subprocess


def genome_extraction(cov: Path, 
                      cutoff: float, 
                      outdir: Path, 
                      prefix: str):
    """
    Only used for metagenomic data. 
    Returns: a list of filtered genome ids.
    The output contains 
    1) <outdir>/indexdb/<prefix>_filtered_genomes.fna: extracted genomes in .fna format, 
    2) <outdir>/indexdb/<prefix>_filtered_bt2index: extracted genomes as a bowtie2 genome index,
    3) <outdir>/indexdb/<prefix>_filtered_coverages.tsv: iltered converage tsv, 
    4) <outdir>/indexdb/<prefix>_filtered_gotu.txt: filtered genome ids. 
    """s
    # create outdir if does not already exist
    subdir = "indexdb"
    if not str(outdir).endswith("indexdb"):
        outdir = Path(outdir) / subdir
    filtered_genome_ids = _genome_filter(cov, cutoff, outdir, prefix)
    output_fna_file = _genome_extract(filtered_genome_ids, ref_db, outdir, prefix)
    _bulid_db(output_fna_file, outdir, prefix)
    return

def _genome_filter(cov: Path,
                   cutoff: float, 
                   outdir: Path, 
                   prefix: str):
    """
    Returns: a list of filtered genome IDs
    Additionally, generate cutoff-based filtered_coverages.tsv, 
    filtered_gotu.txt in <outdir>/indexdb with prefix
    """
    cov = pd.read_csv(cov, sep='\t')
    cov = cov.sort_values(by='coverage_ratio', ascending=False)
    cov_filtered = cov.loc[cov['coverage_ratio'] >= cutoff]
    cov_filtered = cov_filtered.sort_values(by='coverage_ratio', ascending=False)
    gotu_filtered = cov_filtered['gotu']
    # write .tsv and .txt files
    cov_filtered.to_csv(Path(outdir)/f"{prefix}_filtered_coverages.tsv", index=False, header=True, sep='\t')
    gotu_filtered.to_csv(Path(outdir)/f"{prefix}_filtered_gotu.txt", index=False, header=False)
    return gotu_filtered.to_list()
    
def _genome_extract(genome_ids: list,
                    ref_db: Path,
                    outdir: Path,
                    prefix: str):
    """
    Outputs: a .fna file containing filtered genomes
    """
    # load ref db
    open_fna_file = None
    if ref_db.endswith(".fna"):
        open_fna_file = open(ref_db.strip(), 'r')
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
                out_fna.write(line + '\n')
                capture = True
            elif capture:
                out_fna.write(line + '\n')
                capture = False
    return output_fna_file

def _build_db(output_fna_file: Path,
              outdir: Path, 
              prefix: str):
    """
    Returns:
        a bowtie2 index with predefined prefix
    """
    # create directory for bt2 index
    output_bt2_dir = outdir + f"/{prefix}_filtered_bt2index"
    pathlib.Path(output_bt2_dir).mkdir(parents=True, exist_ok=True)

    commands = [
        "bowtie2-build", output_fna_file, f"{output_bt2_dir}/{prefix}",
        "--large-index"
    ]

    p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        logging.error(f'{prefix} indexdb failed with code {p.returncode} and error {error}')
    else:
        logging.info(f'{prefix} indexdb finished')

    return


if __name__ == '__main__':
    genome_extraction()
