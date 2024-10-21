import logging
import subprocess
import tempfile
from glob import glob
import os
from mopp.modules.utils import create_folder_without_clear
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import sys


logger = logging.getLogger("mopp")


def plot_genome_density(input, output_dir):
    cov = pd.read_csv(input, sep="\t")
    cov_sorted = cov.sort_values(by="percent_covered", ascending=False)
    filtered_cov = cov_sorted[cov_sorted["percent_covered"] > 0]["percent_covered"]

    kde = gaussian_kde(filtered_cov, bw_method=0.05)
    x = np.linspace(0.9, 101.1, 10000)
    kde_values = kde.evaluate(x)

    threshold = 3
    mask = x > threshold
    x_filtered = x[mask]
    kde_values_filtered = kde_values[mask]

    plt.figure(figsize=(10, 6))
    plt.fill_between(x_filtered, kde_values_filtered, color="#4c9390", alpha=0.8)
    print(kde_values.max())
    plt.ylim(kde_values_filtered.min(), min(kde_values.max() + 0.05, 1.2))
    plt.xlabel(f"Genome Coverage ({threshold}-100%)")
    plt.ylabel("Density")
    plt.xticks(range(0, 100, 10))
    plt.xlim(threshold, 100)
    plt.title(f"Density Plot of Genome Coverage")

    inset_axes = plt.axes([0.6, 0.6, 0.2, 0.2])
    inset_axes.fill_between(x, kde_values, color="#4c9390", alpha=0.8)

    inset_axes.set_xlim(0, 100)
    inset_axes.set_xlabel(f"Genome Coverage (0-100%)")
    inset_axes.set_ylabel(f"Density")
    inset_axes.set_ylim(kde_values.min(), 1)
    inset_axes.axvline(x=3, color="red", linestyle="--")

    plt.savefig(output_dir + "/density.png", dpi=300, bbox_inches="tight")


def plot_effect_of_filteration(input, output_dir):
    df = pd.read_csv(input, sep="\t")
    percent_covered = df["percent_covered"]
    percent_covered_sorted = sorted(percent_covered)  # #Prepare data to plot
    x_vals = []
    y_vals = (
        []
    )  # #We count how many OGUs are within a given within each threshold (1-100%). This creates the curve that informs us at which threshold we have a significant drop in OGUs.
    for min_coverage in percent_covered_sorted:
        num_remaining = sum(percent_covered >= min_coverage)
        x_vals.append(min_coverage)
        y_vals.append(num_remaining)
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, y_vals, linewidth=2.0)
    plt.yscale("log")
    plt.xlabel("Minimum Coverage Percentage")
    plt.ylabel("Number of OGUs remaining")
    plt.title("Effect of Coverage Filtration on OGU count")
    plt.grid(True)
    plt.savefig(
            output_dir + "/feature_vs_coverage.png", dpi=300, bbox_inches="tight"
        )


def calculate_coverages(input_dir, output_dir, genome_lengths):
    create_folder_without_clear(output_dir)

    output_file = output_dir + "/coverage_calculation.tsv"

    files = glob(os.path.join(input_dir, "*.sam.xz"))
    if files:
        file_list = " ".join(files)
        cmd = f"xzcat {file_list} | micov compress --output {output_file} --lengths {genome_lengths}"

    else:

        files = glob(os.path.join(input_dir, "*.sam"))
        if files:
            file_list = " ".join(files)
            cmd = f"cat {file_list} | micov compress --output {output_file} --lengths {genome_lengths}"
        else:
            logger.error("No sam or sam.xz files found")
            sys.exit(1)


    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    output, error = p.communicate()
    if p.returncode != 0:
        err = f"Calculate coverages failed with code {p.returncode} and error {error.decode('utf-8')}"
        logger.error(err)
    else:
        logger.info(f"Calculate coverages finished")
        plot_genome_density(output_file, output_dir)  
        plot_effect_of_filteration(output_file, output_dir)


