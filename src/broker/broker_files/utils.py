import json
import logging
import pathlib

from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.time import Time
from ligo.skymap.io import read_sky_map
from ligo.skymap.postprocess import crossmatch
import numpy as np


with open(pathlib.Path(__file__).absolute().parent / 'data/GW170817.json') as f:
    gw170817_data = json.load(f)

gw170817_coalescence_time = Time('2017-08-17T12:41:04', format='isot',
                                 scale='utc')
"""Time of coalescence GW170817"""

gw_170817_coord = SkyCoord(
    gw170817_data['GW170817']['ra'][0]['value'],
    gw170817_data['GW170817']['dec'][0]['value'],
    unit=(u.hourangle, u.deg))
"""Sky coordinates of NGC4993"""

gw170817_photometry = gw170817_data['GW170817']['photometry']
"""Dictionary containing instrument-specific photometry"""

_instrument_property_assoc = {
    'Swope': 'instrument',
    'LCO 1m': 'telescope',
    'DECam': 'instrument',
    'HST': 'instrument',
    'Magellan': 'telescope',
    'PS1': 'instrument'
}


def get_skymap_crossmatch_with_gw170817(skymap_filename):
    crossmatch_result = crossmatch(
        read_sky_map(skymap_filename, moc=True),
        coordinates=gw_170817_coord,
        contours=(0.5, 0.9)
    )
    p_val  = crossmatch_result.probdensity
    offset = crossmatch_result.offset
    area_fifty, area_ninety = crossmatch_result.contour_areas
    return p_val, offset, area_fifty, area_ninety


def get_photometry(instrument):
    try:
        prop = _instrument_property_assoc[instrument]
    except KeyError:
        raise NotImplementedError("Supported instruments: ",
                                  _instrument_property_assoc.keys())
    # FIXME: assume bands in g, r, i
    # match band string names, not being an upperlimit, and MJD after
    # merger time
    r_band = filter(
            lambda x: x.get('band') == 'r' and \
                ~hasattr(x, 'upperlimit') and \
                float(x.get('time', 0)) > gw170817_coalescence_time.mjd and \
                x.get(prop) == instrument,
            gw170817_photometry)

    g_band = filter(
            lambda x: x.get('band') == 'g' and \
                ~hasattr(x, 'upperlimit') and \
                float(x.get('time', 0)) > gw170817_coalescence_time.mjd and \
                x.get(prop) == instrument,
            gw170817_photometry)

    i_band = filter(
            lambda x: x.get('band') == 'i' and \
                ~hasattr(x, 'upperlimit') and \
                float(x.get('time', 0)) > gw170817_coalescence_time.mjd and \
                x.get(prop) == instrument,
            gw170817_photometry)
    return list(g_band), list(r_band), list(i_band)


def get_mag_mag_err_time(g_band_data, r_band_data, i_band_data,
                         lim_mag=20.5):
    mag_g = np.array([_.get('magnitude') for _ in g_band_data]).astype(float)
    mag_err_g = np.array([_.get('e_magnitude') for _ in g_band_data]).astype(float)
    mjd_g = np.array([_.get('time') for _ in g_band_data]).astype(float)
    mask_g = mag_g < lim_mag
    mag_g = mag_g[mask_g]
    mag_err_g = mag_err_g[mask_g]
    mjd_g = mjd_g[mask_g]

    mag_r = np.array([_.get('magnitude') for _ in r_band_data]).astype(float)
    mag_err_r = np.array([_.get('e_magnitude') for _ in r_band_data]).astype(float)
    mjd_r = np.array([_.get('time') for _ in r_band_data]).astype(float)
    mask_r = mag_r < lim_mag
    mag_r = mag_r[mask_r]
    mag_err_r = mag_err_r[mask_r]
    mjd_r = mjd_r[mask_r]

    mag_i = np.array([_.get('magnitude') for _ in i_band_data]).astype(float)
    mag_err_i = np.array([_.get('e_magnitude') for _ in i_band_data]).astype(float)
    mjd_i = np.array([_.get('time') for _ in i_band_data]).astype(float)
    mask_i = mag_i < lim_mag
    mag_i = mag_i[mask_i]
    mag_err_i = mag_err_i[mask_i]
    mjd_i = mjd_i[mask_i]

    return (mjd_g, mjd_r, mjd_i, mag_g, mag_r, mag_i,
            mag_err_g, mag_err_r, mag_err_i)


def get_flux_from_mag(mag_g, mag_r, mag_i,
                      mag_err_g, mag_err_r, mag_err_i,
                      zeropoint=27.5):
    fluxcal_r = 10**(-0.4 * (mag_r - zeropoint))
    fluxcal_g = 10**(-0.4 * (mag_g - zeropoint))
    fluxcal_i = 10**(-0.4 * (mag_i - zeropoint))
    fluxcal_err_r = np.nan_to_num(mag_err_r, nan=1000) / 1.09 * fluxcal_r
    fluxcal_err_g = np.nan_to_num(mag_err_g, nan=1000) / 1.09 * fluxcal_g
    fluxcal_err_i = np.nan_to_num(mag_err_i, nan=1000) / 1.09 * fluxcal_i
    return (fluxcal_g, fluxcal_r, fluxcal_i,
            fluxcal_err_g, fluxcal_err_r, fluxcal_err_i)


def get_data_for_gw170817(instrument, lim_mag, num_obs=-1, skip_every=1):
    """Get the photometry for a particular instrument"""
    g_band_data, r_band_data, i_band_data = get_photometry(instrument)

    mjd_g, mjd_r, mjd_i, mag_g, mag_r, mag_i, mag_err_g, mag_err_r, mag_err_i = \
        get_mag_mag_err_time(g_band_data, r_band_data, i_band_data, lim_mag=lim_mag)
    
    flux_g, flux_r, flux_i, flux_err_g, flux_err_r, flux_err_i = get_flux_from_mag(
        mag_g, mag_r, mag_i, mag_err_g, mag_err_r, mag_err_i
    )

    # put into a dataframe
    mjd = np.hstack((mjd_g, mjd_r, mjd_i))  # stack times
    gw_trigger_mjd = gw170817_coalescence_time.mjd
    mjd -= gw_trigger_mjd

    # stack data and sort based on mjd
    flux = np.hstack((flux_g, flux_r, flux_i))
    fluxerr = np.hstack((flux_err_g, flux_err_r, flux_err_i))

    # SNANA lingo; 4096 is a detection, 6144 is the trigger
    photflag_r = np.array(['4096'] * len(flux_r), dtype=int)
    photflag_g = np.array(['4096'] * len(flux_g), dtype=int)
    photflag_i = np.array(['4096'] * len(flux_i), dtype=int)
    photflag = np.hstack((photflag_g, photflag_r, photflag_i))
    passbands = np.array(mjd_g.size*['g'] + mjd_r.size*['r'] + mjd_i.size*['i'])

    # sort all data based on time
    sort_mask = np.argsort(mjd)
    mjd = mjd[sort_mask]
    flux = flux[sort_mask]
    fluxerr = fluxerr[sort_mask]
    passbands = passbands[sort_mask]
    photflag = photflag[sort_mask]

    # set the very first observation as the trigger
    photflag[0] = '6144'

    objid = "AT2017gfo"
    ra = gw_170817_coord.ra.deg
    dec = gw_170817_coord.dec.deg
    redshift = 0.01  # not used, but to be supplied to classify
    mwebv = 0.07  # not used, but to be supplied to classify

    return (mjd[::skip_every][:num_obs], flux[::skip_every][:num_obs],
            fluxerr[::skip_every][:num_obs], passbands[::skip_every][:num_obs],
            photflag[::skip_every][:num_obs], ra, dec, objid, redshift, mwebv)


def get_logger(logger_name, fmt='%(asctime)s [%(levelname)s] '
                                '%(name)s: %(message)s'):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    return logger