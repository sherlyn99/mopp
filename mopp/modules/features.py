import os
import logging
import subprocess
from pathlib import Path
from mopp.modules.utils import create_folder_without_clear

logger = logging.getLogger("mopp")


# mopp features \
#   -i <sam_dir> \
#   -o <out_dir> \
#   -strat \
#   -tax map (optional) \
#   -func map (optional)


def gen_feature_table(
    indir,
    outdir,
    suffix,
    strat,
    coords_map,
    tax_map,
    func_map,
    divide,
    names=None,
):
    if not suffix:
        raise ValueError("Suffix must be provided.")
    else:
        suffix = suffix.lstrip(".")

    Path(outdir).mkdir(parents=True, exist_ok=True)
    file_ogu = f"{outdir}/ogu.{suffix}"
    file_tax = f"{outdir}/tax.{suffix}"
    file_ogu_orf = f"{outdir}/ogu_orf.{suffix}"
    file_tax_orf = os.path.join(outdir, f"tax_orf.{suffix}")
    file_tax_func = os.path.join(outdir, f"tax_func.{suffix}")
    file_ogu_func = os.path.join(outdir, f"ogu_func.{suffix}")
    mapdir = os.path.join(outdir, "mapdir")

    if strat:
        if not coords_map:
            raise ValueError(
                "Stratification without coords is not supported. Please specify '--coords'."
            )

        commands = gen_commands_features(
            indir,
            file_ogu_orf,
            mapdir,
            coords_map,
        )
        run_command(commands, f"Generating {file_ogu_orf}")

        if tax_map:

            commands = gen_commands_collapse(
                file_ogu_orf,
                file_tax_orf,
                "|",
                1,
                tax_map,
                divide,
                names,
            )
            run_command(commands, f"Generating {file_tax_orf}")

        if func_map:
            if tax_map:
                commands = gen_commands_collapse(
                    file_tax_orf,
                    file_tax_func,
                    "|",
                    2,
                    func_map,
                    divide,
                    names,
                )
                run_command(commands, f"Generating {file_tax_func}")
            else:
                commands = gen_commands_collapse(
                    file_ogu_orf,
                    file_ogu_func,
                    "|",
                    2,
                    func_map,
                    divide,
                    names,
                )
                run_command(commands, f"Generating {file_ogu_func}")
    else:
        commands = gen_commands_features(
            indir,
            file_ogu,
            mapdir,
            None,
        )
        run_command(commands, f"Generating {file_ogu}")

        if tax_map:
            commands = gen_commands_collapse(
                file_ogu,
                file_tax,
                None,
                None,
                tax_map,
                divide,
                names,
            )
            run_command(commands, f"Generating {file_tax}")

        if func_map:
            raise ValueError(
                "Function map provided without stratification is not supported. Try add '-strat'."
            )


def gen_commands_features(
    indir,
    outfile,
    mapdir,
    coords_map,
):
    commands = [
        "woltka",
        "classify",
        "-i",
        indir,
        "-o",
        outfile,
    ]

    if coords_map:
        commands += ["--coords", coords_map, "--stratify", mapdir]
    else:
        commands += ["--outmap", mapdir]
    return commands


def gen_commands_collapse(infile, outfile, sep, field, map, divide, names):
    commands = [
        "woltka",
        "collapse",
        "-i",
        infile,
        "-o",
        outfile,
        "-m",
        map,
    ]

    if sep and field:
        commands += [
            "-s",
            str(sep),
            "-f",
            str(field),
        ]

    if divide:
        commands += ["--divide"]

    if names:
        commands += ["--name", names]

    return commands


def run_command(commands, message):
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
