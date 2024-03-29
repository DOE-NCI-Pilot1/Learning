"""
Post-processing script.
Learning curve data are generated for different splits of a dataset.
This script aggregates LC results from different runs (i.e., different data splits).
"""
import warnings
warnings.filterwarnings('ignore')

import os
import sys
from pathlib import Path
import argparse
from glob import glob

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

# Utils
from learningcurve.lc_plots import plot_lc_many_metric

# File path
filepath = Path(__file__).resolve().parent


def parse_args(args):
    parser = argparse.ArgumentParser(description='Generate learning curves.')
    parser.add_argument('-r', '--res_dir',
                        required=True,
                        default=None,
                        type=str,
                        help='Global dir where LC data are located (default: None).')
    args, other_args = parser.parse_known_args(args)
    return args


def agg_scores(run_dirs):
    """ Aggregate scores from LC runs. Instead of using lc_scores.csv, load
    scores from scores.csv that located in each split0_sz* folder. """
    scores = []

    for rn_dr in run_dirs:

        sz_dirs = sorted(rn_dr.glob('*_sz*'))
        for sz_dr in sz_dirs:

            dpath = Path(sz_dr, 'scores.csv')
            if not dpath.exists():
                continue

            scr = pd.read_csv(dpath)
            scr['split'] = Path(rn_dr).name
            scores.append(scr)

    scores = pd.concat(scores, axis=0)
    scores = scores.sort_values(['tr_size', 'split']).reset_index(drop=True)
    return scores


def run(args):
    res_dir = Path(args.res_dir).resolve()
    dir_name = res_dir.name

    run_dirs = sorted(res_dir.glob('run*'))
    scores = agg_scores(run_dirs)

    print('Training set sizes:', np.unique(scores.tr_size))

    te_scores = scores[scores['set']=='te'].reset_index(drop=True)
    # te_scores_mae = scores[(scores['metric']=='mean_absolute_error') &
    #                        (scores['set']=='te')].reset_index(drop=True)

    save = True
    if save:
        scores.to_csv(res_dir/'all_scores.csv', index=False)
        te_scores.to_csv(res_dir/'te_scores.csv', index=False)
        # te_scores_mae.to_csv(res_dir/'te_scores_mae.csv', index=False)

    # Plots
    metrics = ['mean_absolute_error', 'r2']

    kwargs = {'tr_set': 'te', 'xtick_scale': 'log2', 'ytick_scale': 'log2'}
    plot_dir = res_dir/'plots_log_scale'
    os.makedirs(plot_dir, exist_ok=True)
    ax = plot_lc_many_metric(scores, metrics=metrics, outdir=plot_dir, **kwargs)

    kwargs = {'tr_set': 'te', 'xtick_scale': 'linear', 'ytick_scale': 'linear'}
    plot_dir = res_dir/'plots_linear_scale'
    os.makedirs(plot_dir, exist_ok=True)
    ax = plot_lc_many_metric(scores, metrics=metrics, outdir=plot_dir, **kwargs)

    return None


def main(args):
    args = parse_args(args)
    run(args)


if __name__ == '__main__':
    main(sys.argv[1:])