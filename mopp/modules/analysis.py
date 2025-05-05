import os
import logging
import subprocess
from pathlib import Path
from mopp.modules.utils import create_folder_without_clear

logger = logging.getLogger("mopp")

def analysis(input, output, uniref_mapping, kegg_mapping):
    commands = [
        "Rscript",
        "./mopp/MIND_script.R",
        input,
        output,
        uniref_mapping,
        kegg_mapping
    ]

    logger.info(f"Feature table analysis started")
    p = subprocess.Popen(
        commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = p.communicate()
    if p.returncode != 0:
        err = f"Feature table analysis failed with code {p.returncode} and error {error.decode('utf-8')}"
        logger.error(err)
    else:
        logger.info(f"Feature table analysis completed")