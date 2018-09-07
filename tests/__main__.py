from unittest import defaultTestLoader
from unittest.runner import TextTestRunner
from os.path import dirname

runner = TextTestRunner()
suite = defaultTestLoader.discover(dirname(__file__))
runner.run(suite)
