#!/usr/bin/env python3
import os
import click
from pathlib import Path

import numpy as np
from astrorapid import Classify

import db_utils, utils

elcid_model_filename = Path(__file__).absolute().parent
elcid_model_filename /= "data/keras_model.hdf5"

log = utils.get_logger(os.path.basename(__file__))

default_kwargs = dict(
    known_redshift=False,
    passbands=('g', 'r', 'i'),
    class_names=('Kilonova', 'Other'),
    mintime=-0.5,
    maxtime=10,
    timestep=0.7,
    nobs=12
)
default_kwargs.update(dict(model_filepath=elcid_model_filename))


def get_classifier(**kwargs):
    if set(default_kwargs) - set(kwargs) != set():
        kwargs.update(default_kwargs)

    return Classify(**kwargs)


def gw170817_classification(lim_mag, num_obs, skip_every):
    # get contextual information from skymap
    p_val, offset, area_fifty, area_ninety = utils.get_skymap_crossmatch_with_gw170817(
        Path(__file__).absolute().parent / 'data/bayestar.flat.fits.gz'
    )
    lightcurve_data = utils.get_gw170817_data_from_database(lim_mag, num_obs,
                                                            skip_every)
    other_meta_data = dict(
        offset=offset,
        logprob=np.log10(p_val),
        area_ninety=area_ninety,
    )
    classifier = get_classifier()
    predictions, time_steps = classifier.get_predictions(
        [lightcurve_data,], return_predictions_at_obstime=True,
        other_meta_data=[other_meta_data,]
    )
    kn_predictions, other_predictions = predictions[0].T
    time_steps = time_steps[0]
    return kn_predictions, other_predictions, time_steps


def _plot(kn_res, other_res, times, lim_mag, instrument='DECam'):
    # plot the lightcurve in one panel and scores in the other
    g_band, r_band, i_band = utils.get_photometry(instrument)
    mjd_g, mjd_r, mjd_i, mag_g, mag_r, mag_i, mag_err_g, mag_err_r, mag_err_i = \
        utils.get_mag_mag_err_time(g_band, r_band, i_band, lim_mag)

    import matplotlib.pyplot as plt
    fig, (axis1, axis2) = plt.subplots(1, 2, figsize=(24, 6))

    axis1.errorbar(mjd_r, mag_r, yerr=mag_err_r,
                color='red', fmt='*', label='R')
    axis1.errorbar(mjd_g, mag_g, yerr=mag_err_g,
                color='green', fmt='^', label='g')
    axis1.errorbar(mjd_i, mag_i, yerr=mag_err_i,
                color='black', fmt='o', label='i')
    axis1.set_ylim(axis1.get_ylim()[::-1])

    axis1.set_xlabel("MJD")
    axis1.set_title(instrument)
    axis1.legend()

    axis2.plot(times, kn_res, 'r-', label='KN class')
    axis2.plot(times, other_res, 'b--', alpha=0.5, label='Other class')
    axis2.set_ylabel("Class score")
    axis2.set_xlabel("Time (days)")
    axis2.set_title("Prediction")
    axis2.legend()
    plt.show()


@click.command()
@click.option('--lim-mag', default=20.5, type=click.FLOAT,
              help="Limiting mag. Dimmer observations are skipped.")
@click.option('--max-num-obs', default=10, type=click.INT,
              help="Number of observations from start")
@click.option('--skip-every', default=1, type=click.INT, help="Skip these many obs.")
@click.option('--plot', is_flag=True, help='Plot results/print to stdout')
@click.option('--db-write', is_flag=True,
              help="Write results to database")
def cli(lim_mag, max_num_obs, skip_every, plot, db_write):
    kn_res, other_res, times = gw170817_classification(lim_mag, max_num_obs,
                                                       skip_every)
    if plot:
        _plot(kn_res, other_res, times, lim_mag)
        return

    if db_write:
        conn = db_utils.DbConnector(
            db_utils.MARIADB_HOSTNAME, db_utils.MARIADB_USER,
            db_utils.MARIADB_PASSWORD, db_utils.MARIADB_DATABASE)
        conn.open_db_connection()
        # fetch existing results and append
        # and write new results based on next time steps
        old_results = conn.get_results_data()
        old_results = np.array(old_results)
        
        data = []
        if old_results.size == 0:
            for time, kn_score, other_score in zip(times, kn_res, other_res):
                data.append(
                    {'time': float(time), 'kn_score': float(kn_score),
                     'other_score': float(other_score)}
                )
        else:
            # get the last entered time
            max_time_in_results_table = np.max(old_results.T[1])
            mask = times > max_time_in_results_table

            relevant_times = times[mask]
            relevant_kn_score = kn_res[mask]
            relevant_other_score = other_res[mask]
            for time, kn_score, other_score in zip(relevant_times,
                                                   relevant_kn_score,
                                                   relevant_other_score):
                data.append(
                    {'time': float(time), 'kn_score': float(kn_score),
                     'other_score': float(other_score)}
                )
        conn.insert_results_data(data)
        conn.close_db_connection()
        return
    print("Times:", times)
    print("KN score:", kn_res)
    print("Other score:", other_res)


if __name__ == '__main__':
    cli()
