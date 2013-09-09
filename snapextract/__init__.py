# -*- coding: utf-8 -*-

"""
Climate indices for geotechnical engineering consideration are
extremely important for designing engineered structures on permanently
frozen and seasonally frozen soils, particularly in Alaska. Relevant
climate indices typically include (over a given timespan) a site's
average air temperature, the average air freezing and air thawing
indices, and the design air freezing and thawing indices (the average
of the three coldest or three warmest years, respectively).

The University of Alaska Fairbanks (UAF) Scenarios Network for Alaska
and Arctic Planning (http://snap.uaf.edu) has prepared and maintains
a geographically gridded dataset representing calculated climate
parameters across Alaska. SNAP provides an estimate of historical
climate conditions in regions of Alaska that do not have consistent
climate records, as well as providing scientifically defined
peer-reviewed climatic projections. Previous methods utilized in
engineering practice for projecting climate indices involved
procedures with no scientific basis (linear extrapolation), and
provided little confidence in the accuracy of the results. As
distributed, the SNAP datasets are extremely large and cumbersome, and
represent a significant hurdle for users to process site-specific
data.

.. moduleauthor:: Matthew Dillon <mrdillon@alaska.edu>
"""

from ._backend import SNAPDataSet, GeoRefData, mkdir_p, wgs84_to_ne, ne_to_wgs
