# -*- coding: utf-8 -*-
"""
Simple tests for snapextract backend.
"""

import snapextract
import nose
from nose.tools import assert_equal
import numpy as np
from numpy.testing import assert_array_almost_equal
import zipfile
import os
import shutil

def test_load_dataset():
    """
    Test for zipfile module support.
    """
    filename = 'raw_data/tas_AK_771m_5modelAvg_sresa1b_2050_2100.zip'
    dataset = snapextract.SNAPDataSet(filename)
    assert_equal(isinstance(dataset.zip_data, zipfile.ZipFile), True)

def test_file_prefix():
    """
    Test that zipfile prefix parsing is correct.
    """
    filename = 'raw_data/tas_AK_771m_5modelAvg_sresa1b_2050_2100.zip'
    dataset = snapextract.SNAPDataSet(filename)
    assert_equal(dataset.prefix, 'tas_mean_C_ar4_5modelAvg_sresa1b_')

def test_file_dir():
    """
    Test that zipfile filenames are parsing correctly.
    """
    filename = 'raw_data/tas_AK_771m_5modelAvg_sresa1b_2050_2100.zip'
    dataset = snapextract.SNAPDataSet(filename)
    assert_equal(dataset.zip_dir, 'tas50_100/')

def test_load_geotiff_as_array():
    """
    Check that geotiff file is correctly extracted from zipfile.
    """
    filename = 'raw_data/tas_AK_771m_5modelAvg_sresa1b_2050_2100.zip'
    dataset = snapextract.GeoRefData(filename)
    temperatures = dataset.read_geotiff_as_array(1, 2051)
    assert_equal(str(type(temperatures))[-15:-2], "numpy.ndarray")

def test_define_geotiff_params():
    """
    Test that GDAL correctly determines geotiff parameters.
    """
    filename = 'raw_data/tas_AK_771m_5modelAvg_sresa1b_2050_2100.zip'
    dataset = snapextract.GeoRefData(filename)
    tiff_info = [dataset.cols, dataset.rows, dataset.bands, dataset.origin_x,
                dataset.origin_y, dataset.pixel_width, dataset.pixel_height]
    actual_tiff = [4762, 2557, 1, -2173225.118142955, 2381118.150470569,
                  771.0, -770.9999999999999]
    assert_equal(tiff_info, actual_tiff)

def test_ne_to_indices():
    """
    Test that conversion of Northings and Eastings to array indices works.
    """
    filename = 'raw_data/tas_AK_771m_5modelAvg_sresa1b_2050_2100.zip'
    dataset = snapextract.GeoRefData(filename)
    northings = np.array([1250935.040000])
    eastings = np.array([214641.356000])
    x_ind, y_ind = dataset.ne_to_indices(northings, eastings)
    assert_equal((x_ind, y_ind), (3097, 1465))

def test_indices_to_ne():
    """
    Test that conversion of array indices to Northings and Eastings works.
    """
    filename = 'raw_data/tas_AK_771m_5modelAvg_sresa1b_2050_2100.zip'
    dataset = snapextract.GeoRefData(filename)
    x_ind = np.array([3097])
    y_ind = np.array([1465])
    northings, eastings = dataset.indices_to_ne(x_ind, y_ind)
    new_x, new_y = dataset.ne_to_indices(northings, eastings)
    assert_equal((x_ind, y_ind), (new_x, new_y))

def test_extract_point_data_1c_1y():
    """
    Extract point temperatures from 1 city, 1 year.
    """
    filename = 'raw_data/tas_AK_771m_CRU_TS31_historical_1950_2009.zip'
    dataset = snapextract.GeoRefData(filename)
    # City,EASTING,NORTHING
    # Anchorage,214641.356000,1250935.040000
    northings = np.array([1250935.040000])
    eastings = np.array([214641.356000])
    startyr = 2009
    endyr = 2009
    # one city per row, one column per month
    # temps in F
    temps = np.array([15.08, 15.98, 24.26, 37.22, 51.08, 56.66,
                          62.06, 57.74, 50.00, 38.48, 18.86, 21.20])
    # temps in C
    temps = (temps - 32.0) * (5.0 / 9.0)
    temps = temps.reshape(1, 12)
    extracted_temps = dataset.extract_points(northings, eastings,
                                             startyr, endyr)
    assert_array_almost_equal(extracted_temps['temperature'], temps)

def test_extract_point_data_2c_1y():
    """
    Extract point temperatures from 2 cities, 1 year.
    """
    filename = 'raw_data/tas_AK_771m_CRU_TS31_historical_1950_2009.zip'
    dataset = snapextract.GeoRefData(filename)
    # City,EASTING,NORTHING
    # Anchorage,214641.356000,1250935.040000
    # Fairbanks,297703.529000,1667062.690000
    northings = np.array([1250935.040000, 1667062.690000])
    eastings = np.array([214641.356000, 297703.529000])
    startyr = 2009
    endyr = 2009
    # temps in F
    temps = np.array([[15.08, 15.98, 24.26, 37.22, 51.08, 56.66,
                         62.06, 57.74, 50.00, 38.48, 18.86, 21.20],
                        [-11.38, -3.28, 9.14, 32.90, 53.42, 61.34,
                         67.64, 55.40, 48.20, 27.14, -2.38, -2.38]])
    # temps in C
    temps = (temps - 32.0) * (5.0 / 9.0)
    temps = temps.reshape(2, 12)
    extracted_temps = dataset.extract_points(northings, eastings,
                                             startyr, endyr)
    assert_array_almost_equal(extracted_temps['temperature'], temps)

def test_raw_output_simple():
    """
    Dumps the extracted points for Fairbanks and Anchorage data to disk.
    """
    filename = 'raw_data/tas_AK_771m_5modelAvg_sresb1_2001_2049.zip'
    dataset = snapextract.GeoRefData(filename)
    # City,EASTING,NORTHING
    # Anchorage,214641.356000,1250935.040000
    # Fairbanks,297703.529000,1667062.690000
    communities = np.array(['Anchorage', 'Fairbanks'], dtype='S100')
    northings = np.array([1250935.040000, 1667062.690000])
    eastings = np.array([214641.356000, 297703.529000])
    startyr = 2001
    endyr = 2001
    extracted_temps = dataset.extract_points(northings, eastings,
                                             startyr, endyr)
    path = 'output/avg_monthly_temps/'
    snapextract.mkdir_p(path)
    shutil.rmtree(path)
    dataset.dump_raw_temperatures(communities, extracted_temps, path)
    file_list = os.listdir(path)
    assert_equal(file_list, ['Anchorage', 'Fairbanks'])

def test_raw_output_simple_from_index():
    """
    Dumps the extracted points for Nigliq Channel data to disk.
    """
    filename = 'raw_data/tas_AK_771m_5modelAvg_sresb1_2001_2049.zip'
    dataset = snapextract.GeoRefData(filename)
    # City,X_IND,Y_IND
    # Nigliq Channel,2967,156
    communities = np.array(['Nigliq Channel'], dtype='S100')
    x_ind = np.array([2967])
    y_ind = np.array([156])
    northings, eastings = dataset.indices_to_ne(x_ind, y_ind)
    startyr = 2001
    endyr = 2001
    extracted_temps = dataset.extract_points(northings, eastings,
                                             startyr, endyr)
    path = 'output/avg_monthly_temps/'
    snapextract.mkdir_p(path)
    shutil.rmtree(path)
    dataset.dump_raw_temperatures(communities, extracted_temps, path)
    file_list = os.listdir(path)
    assert_equal(file_list, ['Nigliq_Channel'])

def test_wgs84_to_ne():
    """
    Check that conversion from WGS84 coordinates to SNAP NE works.
    """
    latitude = 59.046667
    longitude = -158.508611
    easting, northing, elevation = snapextract.wgs84_to_ne(latitude,
                                                                   longitude)
    assert_equal((easting, northing), (-257669.0691295379, 1014443.6452589828))

if __name__ == '__main__':
    nose.main()
