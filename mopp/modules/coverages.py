import logging
from micov._modules import cli_compress
from mopp.modules.utils import create_folder_without_clear
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde


logger = logging.getLogger("mopp")



def plot_genome_density(input, output_dir):
    cov = pd.read_csv(input, sep='\t')
    cov_sorted = cov.sort_values(by='percent_covered', ascending=False)
    filtered_cov = cov_sorted[cov_sorted['percent_covered'] > 0]['percent_covered']

    kde = gaussian_kde(filtered_cov, bw_method=.05)
    x = np.linspace(0.9, 101.1, 10000) 
    kde_values = kde.evaluate(x)

    threshold = 3
    mask = x > threshold
    x_filtered = x[mask]
    kde_values_filtered = kde_values[mask]

    plt.figure(figsize=(10, 6))
    plt.fill_between(x_filtered, kde_values_filtered, color="#4c9390", alpha=0.8)

    plt.ylim(kde_values_filtered.min(), kde_values_filtered.max())
    plt.xlabel(f'Genome Coverage ({threshold}-100%)')
    plt.ylabel('Density')
    plt.xticks(range(0, 100, 10))
    plt.xlim(threshold, 100)
    plt.title(f'Density Plot of Genome Coverage')

    inset_axes = plt.axes([0.6, 0.6, 0.2, 0.2]) 
    inset_axes.fill_between(x, kde_values, color="#4c9390", alpha=0.8)

    inset_axes.set_xlim(0, 100)
    inset_axes.set_xlabel(f'Genome Coverage (0-100%)')
    inset_axes.set_ylabel(f'Density')
    inset_axes.set_ylim(kde_values.min(), kde_values.max())
    inset_axes.axvline(x=3, color='red', linestyle='--')

    plt.savefig(output_dir + '/density.png', dpi=300, bbox_inches='tight')

def plot_effect_of_filteration(input, output_dir):
    df = pd.read_csv(input, sep='\t')
    percent_covered = df['percent_covered']
    percent_covered_sorted = sorted(percent_covered)  # #Prepare data to plot
    x_vals = []
    y_vals = []  # #We count how many OGUs are within a given within each threshold (1-100%). This creates the curve that informs us at which threshold we have a significant drop in OGUs.
    for min_coverage in percent_covered_sorted:
        num_remaining = sum(percent_covered >= min_coverage)
        x_vals.append(min_coverage)
        y_vals.append(num_remaining)
        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, linewidth=2.0)
        plt.yscale('log')  
        plt.xlabel('Minimum Coverage Percentage')
        plt.ylabel('Number of OGUs remaining')
        plt.title('Effect of Coverage Filtration on OGU count')
        plt.grid(True)
        plt.savefig(output_dir + '/filtration_effect.png', dpi=300, bbox_inches='tight')


def calculate_coverages(input_dir, output_dir, genome_lengths):
    create_folder_without_clear(output_dir)

    cli_compress(
        input_dir,
        output_dir + "/cov_percentages.tsv",
        genome_lengths,
        disable_compression=False,
        skip_intermediate=True,
    )

    plot_genome_density(output_dir + "/cov_percentages.tsv", output_dir)
    plot_effect_of_filteration(output_dir + "/cov_percentages.tsv", output_dir)


if __name__ == "__main__":
    calculate_coverages()
