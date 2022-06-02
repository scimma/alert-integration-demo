#!/usr/bin/env python3

import click
from pathlib import Path

import numpy as np
from astrorapid import Classify

import utils

elcid_model_filename = Path(__file__).absolute().parent
elcid_model_filename /= "data/keras_model.hdf5"

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


def gw170817_classification(instrument, lim_mag, num_obs, skip_every):
    # get contextual information from skymap
    p_val, offset, area_fifty, area_ninety = utils.get_skymap_crossmatch_with_gw170817(
        Path(__file__).absolute().parent / 'data/bayestar.flat.fits.gz'
    )
    lightcurve_data = utils.get_data_for_gw170817(instrument, lim_mag,
                                                  num_obs, skip_every)
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


def _plot(kn_res, other_res, times, instrument, lim_mag):
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
@click.option('--instrument', help='Instrument observing GW170817')
@click.option('--lim-mag', default=20.5, type=click.FLOAT,
              help="Limiting mag. Dimmer observations are skipped.")
@click.option('--num-obs', default=10, type=click.INT,
              help="Number of observations from start")
@click.option('--skip-every', default=1, type=click.INT, help="Skip these many obs.")
@click.option('--plot', is_flag=True, help='Plot results/print to stdout')
def cli(instrument, lim_mag, num_obs, skip_every, plot):
    click.echo(f"Classification result for {instrument}")
    kn_res, other_res, times = gw170817_classification(instrument, lim_mag,
                                                       num_obs, skip_every)
    if not plot:
        print("Times:", times)
        print("KN score:", kn_res)
        print("Other score:", other_res)
        return
    _plot(kn_res, other_res, times, instrument, lim_mag)


if __name__ == '__main__':
    cli()
