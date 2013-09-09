************************************
SNAPExtract Documentation and Source
************************************

.. toctree::
   :maxdepth: 4

.. default-domain:: python
.. automodule:: snapextract

SNAPExtract is a Python project, currently supported under version
2.7.x and 3.3.x.

Requirements: gdal, numpy
Option: nose (for testing), sphinx (for docs)

Module: snapextract.backend
---------------------------

Automatic API Documentation.

.. automodule:: snapextract.backend
   :members: SNAPDataSet, GeoRefData

Source: backend.py
^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../snapextract/_backend.py

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
