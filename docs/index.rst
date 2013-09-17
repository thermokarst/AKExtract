**********************************
AKExtract Documentation and Source
**********************************

.. toctree::
   :maxdepth: 4

.. default-domain:: python
.. automodule:: akextract

AKExtract is a Python project, currently supported under version
2.7.x and 3.3.x.

Requirements: gdal, numpy
Option: nose (for testing), sphinx (for docs)

Module: akextract.backend
---------------------------

Automatic API Documentation.

.. automodule:: akextract.backend
   :members: SNAPDataSet, GeoRefData

Source: backend.py
^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../akextract/_backend.py

Tests
-----

Backend - Simple
^^^^^^^^^^^^^^^^

.. automodule:: tests.test_backend_simple
   :members:

Source: test_backend_simple.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../tests/test_backend_simple.py

Backend - Advanced
^^^^^^^^^^^^^^^^^^

.. automodule:: tests.test_backend_advanced
   :members:

Source: test_backend_advanced.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../tests/test_backend_advanced.py

Processing - Simple
^^^^^^^^^^^^^^^^^^^

.. automodule:: tests.test_processing_simple
   :members:

Source: test_processing_simple.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../tests/test_processing_simple.py
