import os
import click
from pathlib import Path

import numpy as np
from astrorapid import Classify

import db_utils, utils
import time

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


def gw170817_classification(lim_mag, num_obs, skip_every, p_val, offset, area_fifty, area_ninety):
    lightcurve_data = utils.get_gw170817_data_from_database(lim_mag, num_obs, skip_every)
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


@click.command()
@click.option('--lim-mag', default=20.5, type=click.FLOAT,
              help="Limiting mag. Dimmer observations are skipped.")
@click.option('--max-num-obs', default=10, type=click.INT,
              help="Number of observations from start")
@click.option('--skip-every', default=1, type=click.INT, help="Skip these many obs.")
def cli(lim_mag, max_num_obs, skip_every):

    while True:
        try:
            conn = db_utils.DbConnector(
                db_utils.MARIADB_HOSTNAME, db_utils.MARIADB_USER,
                db_utils.MARIADB_PASSWORD, db_utils.MARIADB_DATABASE)
        except:
            log.info('Waiting for database...')
            time.sleep(5)
            continue
        else:
            break

    CLASSIFY_WAIT_TIME = float(os.getenv('CLASSIFY_WAIT_TIME', 1))

    # get static contextual information from skymap
    p_val, offset, area_fifty, area_ninety = utils.get_skymap_crossmatch_with_gw170817(
        Path(__file__).absolute().parent / 'data/bayestar.flat.fits.gz'
    )
    
    photometry_current_id = 0

    while True:
        try:
            ## Check for new photometry data
            conn.open_db_connection()
            photometry_latest_id = conn.get_photometry_latest_id()
            conn.close_db_connection()
            log.info(f'''photometry_latest_id:  {photometry_latest_id}...''')
            if photometry_current_id == photometry_latest_id:
                log.info(f'''Awaiting new photometry data...''')
                time.sleep(CLASSIFY_WAIT_TIME)
                continue
            else:
                photometry_current_id = photometry_latest_id
            
            ## Classify event based on all available data in the database
            kn_res, other_res, times = gw170817_classification(
                lim_mag,
                max_num_obs,
                skip_every,
                p_val,
                offset,
                area_fifty,
                area_ninety
            )

            conn.open_db_connection()
            # fetch existing results and append
            # and write new results based on next time steps
            old_results = conn.get_results_data()
            old_results = np.array(old_results)
            
            data = []
            if old_results.size == 0:
                for time_obs, kn_score, other_score in zip(times, kn_res, other_res):
                    data.append({
                        'time': float(time_obs),
                        'kn_score': float(kn_score),
                        'other_score': float(other_score),
                        'uuid': utils.generate_uuid(),
                        'candidate': 'GW170817',
                        'ra': float(utils.gw_170817_coord.ra.deg),
                        'dec': float(utils.gw_170817_coord.dec.deg),
                    })
            else:
                # get the last entered time
                max_time_in_results_table = np.max(old_results.T[1])
                mask = times > max_time_in_results_table

                relevant_times = times[mask]
                relevant_kn_score = kn_res[mask]
                relevant_other_score = other_res[mask]
                for time_obs, kn_score, other_score in zip(relevant_times, relevant_kn_score, relevant_other_score):
                    data.append({
                        'time': float(time_obs),
                        'kn_score': float(kn_score),
                        'other_score': float(other_score),
                        'uuid': utils.generate_uuid(),
                        'candidate': 'GW170817',
                        'ra': float(utils.gw_170817_coord.ra.deg),
                        'dec': float(utils.gw_170817_coord.dec.deg),
                    })
            conn.insert_results_data(data)
            conn.close_db_connection()

            # log.info(f'''Times: {times}''')
            # log.info(f'''KN score: {kn_res}''')
            # log.info(f'''Other score: {other_res}''')
        except Exception as e:
            log.error(f'''{e}''')
        
        time.sleep(CLASSIFY_WAIT_TIME)


if __name__ == '__main__':
    cli()
