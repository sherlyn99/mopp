import logging
import subprocess
from pathlib import Path


logger = logging.getLogger("mopp")


def calculate_genome_coverages(zebra_path, indir, outdir):
    calculate_coverages_command = _commands_generation_coverages(zebra_path, indir, outdir)
    p = subprocess.Popen(calculate_coverages_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        err = 'calculation of genome coverages failed with code {p.returncode} and error {error}'
        logging.error(err)
    else:
        logging.info('calculation of genome coverages finished')


def _commands_generation_coverages(zebra_path, indir, outdir):
    path_zebra_calculate_cov = Path(zebra_path) / "calculate_coverages.py"
    path_zebra_wol_md = Path(zebra_path) / "databases" / "WoL" / "metadata.tsv"
    path_indir = Path(indir) # only samflies will be used
    path_outdir_cov = Path(outdir) / "calculate_coverages.tsv"
    commands = [
        "python", str(path_zebra_calculate_cov),
        "-i", str(path_indir),
        "-o", str(path_outdir_cov),
        "-d", str(path_zebra_wol_md)
    ]
    return commands