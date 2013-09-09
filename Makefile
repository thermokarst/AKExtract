init:
	pip install -r requirements.txt --use-mirrors

test2:
	nosetests-2.7 tests

test3:
	nosetests-3.3 tests

simple_test2:
	nosetests-2.7 tests/test_backend_simple.py

advanced_test2:
	nosetests-2.7 tests/test_backend_advanced.py

simple_test3:
	nosetests-3.3 tests/test_backend_simple.py

advanced_test3:
	nosetests-3.3 tests/test_backend_advanced.py
