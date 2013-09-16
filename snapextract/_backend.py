# -*- coding: utf-8 -*-

"""
.. :module:: backend
   :platform: Unix
   :synopsis: This represents the main engine for extracting from the
              raw datasets.

.. moduleauthor:: Matthew Dillon <mrdillon@alaska.edu>
"""

import zipfile
import gdal
import numpy
import itertools
import os
import errno
from osgeo import osr
import sqlite3
import shutil


# Classes
class SNAPDataSet:
    """
    Tools to work with a SNAP Dataset.

    :param filename: A ZIP dataset from SNAP
    """
    def __init__(self, filename):
        self.filename = filename
        self.zip_data = self.load_dataset()
        self.name_list = sorted(self.zip_data.namelist())
        # At this point, all SNAP datasets are zipped in a directory
        self.zip_dir = self.name_list[0]
        # Prefix in the form xyz_mean_C_abc_model_ (month_year.tif following)
        self.prefix = self.name_list[1][len(self.zip_dir):-11]

        # Assume some info about dataset from the filename
        components = filename.replace('.', '_').split('_')[:-1]

        if 'historical' in components:
            # HISTORICAL DATA
            self.model = 'CRU'
            self.scenario = components[components.index('CRU') + 1]
            self.resolution = components[components.index('CRU') - 1]
        else:
            # PROJECTION DATA
            for comp in components:
                if comp == 'AK':
                    startmarker = components.index(comp) + 2
                if comp.startswith('sres'):
                    self.scenario = comp.replace('sres', '').upper()
                    endmarker = components.index(comp)
            self.model = "_".join(components[startmarker:endmarker])
            self.resolution = components[startmarker - 1]


    def load_dataset(self):
        """
        Import ZIP dataset.

        :returns: A reference to a zipfile
        """
        return zipfile.ZipFile(self.filename,"r")


    def dump_raw_temperatures(self, communities, extracted_temps, out):
        """
        Given a set of extracted temperatures, generate csv output of data.

        :param communities: Python list of community names
        :param extracted_temps: Numpy array with extracted temps
        :param out: path to output directory
        """
        min_year = numpy.min(extracted_temps['year'])
        max_year = numpy.max(extracted_temps['year'])
        time_years = max_year - min_year + 1
        i = 0
        for community in communities:
            community = community.decode('utf-8')
            community = community.replace(" ", "_")
            outdir = ''.join([out, '/', community])
            mkdir_p(outdir)
            outfile = ''.join([outdir, '/', community, '_',
                               self.model, '_', self.scenario, '_',
                               str(min_year), '_',
                               str(max_year),'.txt'])
            header = ' '.join([community.replace("_", " "), ',', str(min_year),
                               '-', str(max_year), '\nAverage Monthly' \
                               ' Air Temperature (deg C)\nYear, ' \
                               'Jan, Feb, Mar, Apr, May, Jun, Jul, ' \
                               'Aug, Sep, Oct, Nov, Dec'])
            temp_data = extracted_temps[i, :]['temperature'].reshape(time_years,
                                                                     12)
            file_data = numpy.zeros((time_years, 13))
            file_data[:, 1:] = temp_data
            file_data[:, 0] = numpy.arange(min_year, max_year+1)
            numpy.savetxt(outfile, file_data, fmt=('%d', '%7.1f', '%7.1f',
                                                   '%7.1f', '%7.1f', '%7.1f',
                                                   '%7.1f', '%7.1f', '%7.1f',
                                                   '%7.1f', '%7.1f', '%7.1f',
                                                   '%7.1f'),
                          delimiter=',', header=header)
            i += 1


class GeoRefData(SNAPDataSet):
    """
    Use GDAL to work with the SNAP datasets.

    :param SNAPDataSet: A SNAPDataSet object
    """
    def __init__(self, filename):
        SNAPDataSet.__init__(self, filename)
        test_tiff = self.read_geotiff_as_gdal(1, int(self.filename[-13:-9]))
        self.cols = test_tiff.RasterXSize
        self.rows = test_tiff.RasterYSize
        self.bands = test_tiff.RasterCount
        geotransform = test_tiff.GetGeoTransform()
        self.origin_x = geotransform[0]
        self.origin_y = geotransform[3]
        self.pixel_width = geotransform[1]
        self.pixel_height = geotransform[5]
        # Close the file
        test_tiff = None


    def read_geotiff_as_gdal(self, month, year):
        """
        Read GeoTIFF Data in from ZIP dataset.

        :param month: desired month (1- or 2-digit integer)
        :param year: desired year (4-digit integer)
        :returns: A GDAL data object
        """
        # A bit clunky, but here we assemble a SNAP-style geotiff filename
        tiff = ''.join(['/vsizip/', self.filename, '/', self.zip_dir,
                          self.prefix, str(month).zfill(2), '_',str(year),
                          '.tif'])
        gdal_data = gdal.Open(tiff)
        return gdal_data


    def read_geotiff_as_array(self, month, year):
        """
        Read GeoTIFF Data in from ZIP dataset.

        :param month: desired month (1- or 2-digit integer)
        :param year: desired year (4-digit integer)
        :returns: A Numpy array
        """
        gdal_data = self.read_geotiff_as_gdal(month, year)
        temp_band = gdal_data.GetRasterBand(1)
        temp_data = temp_band.ReadAsArray(0, 0, self.cols, self.rows)
        temp_band = None
        gdal_data = None
        return temp_data


    def ne_to_indices(self, northing, easting):
        """
        Convert Northings and Eastings (NAD 83 Alaska Albers Equal Area
        Conic) to X,Y array indices.

        :param northing: position northing (in meters)
        :param easting: position easting (in meters)
        :returns: array indices that correspond to location
        """
        x_ind = (easting - self.origin_x)/self.pixel_width
        y_ind = (northing - self.origin_y)/self.pixel_height
        x_ind = x_ind.astype(numpy.int, copy=False)
        y_ind = y_ind.astype(numpy.int, copy=False)
        return (x_ind, y_ind)


    def indices_to_ne(self, x_ind, y_ind):
        """
        Convert index values to Northings and Eastings (NAD 83 Alaska Albers
        Equal Area Conic).

        :param x_ind: array x-index
        :param y_ind: array y-index
        :returns: position northings and eastings (in meters) corresponding to
                  location
        """
        northing = self.origin_y + (y_ind * self.pixel_height)
        easting = self.origin_x + (x_ind * self.pixel_width)
        return (northing, easting)


    def extract_points(self, northing, easting, start_year, end_year):
        """
        Extract points from range of years between start and end at the
        specified points (Jan->Dec). Point locations should be numpy arrays.

        :param northing: position northing (in meters)
        :param easting: position easting (in meters)
        :param start_year: 4-digit year for start of analysis period
        :param end_year: 4-digit year for end of analysis period, same as
                         start_year if only analyzing one year
        :returns: numpy array of extracted temperatures
        """
        x_offsets, y_offsets = self.ne_to_indices(northing, easting)
        years = list(range(start_year, end_year + 1))
        months = list(range(1, 13))
        # Record structure: (Year, Month, Temperature)
        # Each row represents a community, each column is a monthly temp.
        extracted_temps = numpy.zeros((len(x_offsets), 12*len(years)),
                                      dtype={'names': ['year', 'month',
                                                       'temperature'],
                                      'formats':['i4', 'i4', 'f4']})
        i = 0
        for year, month in itertools.product(years, months):
        #for year in years:
        #    for month in months:
            temp_data = self.read_geotiff_as_array(month, year)
            # gdal rotates for some reason, so y,x
            extracted_temps[:, i]['temperature'] = temp_data[y_offsets,
                                                             x_offsets]
            extracted_temps[:, i]['year'] = year
            extracted_temps[:, i]['month'] = month
            i += 1
        return extracted_temps


# Functions
def mkdir_p(path):
    """
    Function to emulate mkdir -p functionality.
    Pulled from: http://stackoverflow.com/q/600268/313548

    :param path: path to create new directory at
    :returns: creates a path at the desired location, if one does not already
              exist
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def wgs84_to_ne(latitude, longitude):
    """
    Convert WGS84 lat/long to Northings and Eastings (NAD 83 Alaska Albers
    Equal Area Conic)

    :param latitude: WGS84 latitude (in decimal degrees)
    :param longitude: WGS84 longitude (in decimal degrees)
    :returns: transformed coordinates to Alaska Albers
    """
    wgspoint = osr.SpatialReference()
    wgspoint.ImportFromEPSG(4326)
    nepoint = osr.SpatialReference()
    nepoint.ImportFromEPSG(3338)
    transform = osr.CoordinateTransformation(wgspoint, nepoint)
    return transform.TransformPoint(longitude, latitude)


def ne_to_wgs(northing, easting):
    """
    Convert Northings and Eastings (NAD 83 Alaska Albers
    Equal Area Conic) to WGS84 lat/long .

    :param northing: AK Albers in meters
    :param easting: AK Albers in meters
    :returns: transformed coordinates in WGS84 lat long
    """
    wgspoint = osr.SpatialReference()
    wgspoint.ImportFromEPSG(4326)
    nepoint = osr.SpatialReference()
    nepoint.ImportFromEPSG(3338)
    transform = osr.CoordinateTransformation(nepoint, wgspoint)
    return transform.TransformPoint(easting, northing)


if __name__ == '__main__':
    print("nothing to see here...")
