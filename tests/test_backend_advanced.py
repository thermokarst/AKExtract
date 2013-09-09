# -*- coding: utf-8 -*-

"""Advanced tests for snapextract backend."""

import snapextract
import nose
from nose.tools import assert_equal
import numpy as np
from numpy.testing import assert_array_almost_equal
import shutil
import os

def test_extract_point_data_1c_59y():
    """
    Similar to test_extract_point_data_1c_1y, except this test runs the
    whole range of years in a SNAP dataset.
    """
    filename = 'raw_data/tas_AK_771m_CRU_TS31_historical_1950_2009.zip'
    dataset = snapextract.GeoRefData(filename)
    # City,EASTING,NORTHING
    # Anchorage,214641.356000,1250935.040000
    northings = np.array([1250935.040000])
    eastings = np.array([214641.356000])
    startyr = 1950
    endyr = 2009
    # temps in F
    temps = np.loadtxt('tests/data/anc1950-2009.csv', delimiter=',')
    temps = np.reshape(temps, (1, 720))
    # temps in C
    temps = (temps - 32.0)*(5.0/9.0)
    extracted_temps = dataset.extract_points(northings, eastings,
                                             startyr, endyr)
    assert_array_almost_equal(extracted_temps['temperature'], temps)

def test_extract_point_data_2c_59y():
    """
    Similar to test_extract_point_data_2c_1y, except this test runs the
    whole range of years in a SNAP dataset.
    """
    filename = 'raw_data/tas_AK_771m_CRU_TS31_historical_1950_2009.zip'
    dataset = snapextract.GeoRefData(filename)
    # City,EASTING,NORTHING
    # Anchorage,214641.356000,1250935.040000
    # Fairbanks,297703.529000,1667062.690000
    northings = np.array([1250935.040000, 1667062.690000])
    eastings = np.array([214641.356000, 297703.529000])
    startyr = 1950
    endyr = 2009
    # temps in F
    temps_anc = np.loadtxt('tests/data/anc1950-2009.csv', delimiter=',')
    temps_fbx = np.loadtxt('tests/data/fbx1950-2009.csv', delimiter=',')
    temps = np.zeros((2, 720))
    temps[0, :] = temps_anc.flatten()
    temps[1, :] = temps_fbx.flatten()
    # temps in C
    temps = (temps - 32.0)*(5.0/9.0)
    extracted_temps = dataset.extract_points(northings, eastings,
                                             startyr, endyr)
    assert_array_almost_equal(extracted_temps['temperature'], temps, decimal=3)

def test_raw_output_all_communities():
    """
    Dumps *ALL* of the extracted points to disk.
    """
    filename = 'raw_data/tas_AK_771m_5modelAvg_sresb1_2001_2049.zip'
    dataset = snapextract.GeoRefData(filename)
    dt = np.dtype({'names':['community', 'northing', 'easting'],
                      'formats':['S100', 'f8', 'f8']})
    community_file = 'tests/data/communities_dist.csv'
    communities, eastings, northings = np.loadtxt(community_file,
                                                     skiprows=1, delimiter=',',
                                                     unpack=True, dtype=dt)
    communities = communities.tolist()

    startyr = 2001
    endyr = 2001
    extracted_temps = dataset.extract_points(northings, eastings,
                                             startyr, endyr)
    path = 'output/avg_monthly_temps/'
    snapextract.mkdir_p(path)
    shutil.rmtree(path)
    dataset.dump_raw_temperatures(communities, extracted_temps, path)
    file_list = os.listdir(path)
    communities.sort()
    file_list.sort()
    mismatches = []
    i = 0
    for item in communities:
        if item.decode('utf-8') != file_list[i].replace("_", " "):
            mismatches.append((item, file_list[i].replace("_", " ")))
        i += 1

    assert_equal(len(mismatches), 0)


if __name__ == '__main__':
    nose.main()
