import xmlrunner
import unittest

xmlrunner.XMLTestRunner(output="tests_results").run(unittest.TestLoader().discover("./tests"))
