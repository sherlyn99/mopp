import logging
import subprocess
from pathlib import Path
from mopp.modules.utils import create_folder_without_clear

logger = logging.getLogger("mopp")


def ft_generation(indir, outdir, db, rank: list, stratification):
    outdir = Path(outdir)
    create_folder_without_clear(outdir)

    if "genus" in rank:
        message = "genus level feature table generation"
        commands = _commands_generation_woltka("genus", indir, outdir, db)
        logger.info(f"{message} started")
        p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()
        if p.returncode != 0:
            logger.error(
                f"{message} failed with code {p.returncode} and error {error.decode('utf-8')}"
            )
        else:
            logger.info(f"{message} finished")

        if stratification:
            message = "genus-uniref stratified feature table generation"
            commands = _commands_stratification_generation_woltka(
                "genus", indir, outdir, db
            )
            logger.info(f"{message} started")
            p = subprocess.Popen(
                commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output, error = p.communicate()
            if p.returncode != 0:
                logger.error(
                    f"{message} failed with code {p.returncode} and error {error.decode('utf-8')}"
                )
            else:
                logger.info(f"{message} finished")

    if "species" in rank:
        message = "species level feature table generation"
        commands = _commands_generation_woltka("species", indir, outdir, db)
        logger.info(f"{message} started")
        p = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()
        if p.returncode != 0:
            logger.error(
                f"{message} failed with code {p.returncode} and error {error.decode('utf-8')}"
            )
        else:
            logger.info(f"{message} finished")

        if stratification:
            message = "species-uniref stratified feature table generation"
            commands = _commands_stratification_generation_woltka(
                "species", indir, outdir, db
            )
            logger.info(f"{message} started")
            p = subprocess.Popen(
                commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output, error = p.communicate()
            if p.returncode != 0:
                logger.error(
                    f"{message} failed with code {p.returncode} and error {error.decode('utf-8')}"
                )
            else:
                logger.info(f"{message} finished")
    return


def _commands_generation_woltka(rank: str, indir, outdir, db):
    commands = [
        "woltka",
        "classify",
        "--input",
        indir,
        "--map",
        f"{db}/taxonomy/taxid.map",
        "--nodes",
        f"{db}/taxonomy/nodes.dmp",
        "--names",
        f"{db}/taxonomy/names.dmp",
        "--rank",
        rank,
        "--name-as-id",
        "--outmap",
        f"{outdir}/{rank}_level/mapdir",
        "--output",
        f"{outdir}/{rank}_level/counts_{rank}.tsv",
    ]
    return commands


def _commands_stratification_generation_woltka(rank: str, indir, outdir, db):
    commands = [
        "woltka",
        "classify",
        "--input",
        indir,
        "--coords",
        f"{db}/proteins/coords.txt.xz",
        "--map",
        f"{db}/function/uniref/uniref.map.xz",
        "--map",
        f"{db}/function/go/process.map.xz",
        "--map-as-rank",
        "--rank",
        "process",
        "-n",
        f"{db}/function/uniref/uniref.name.xz",
        "-r",
        "uniref",
        "--stratify",
        f"{outdir}/{rank}_level/mapdir",
        "--output",
        f"{outdir}/{rank}_level/counts_{rank}_stratified.tsv",
    ]
    return commands


if __name__ == "__main__":
    ft_generation()
