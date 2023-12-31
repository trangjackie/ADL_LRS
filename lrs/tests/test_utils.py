import unittest
import sys

sys.path.append("../..")

from datetime import datetime
from ..utils.time import last_modified_from_statements

class TestUtilityMethods(unittest.TestCase):

    def test_last_modified_helper(self):

        expected_time = datetime.utcnow()
        expected_time_str = expected_time.isoformat()

        statements = [
            { "stored": expected_time_str },
            { "stored": expected_time_str }
        ]

        last_modified = last_modified_from_statements(statements)

        self.assertTrue(expected_time == last_modified)

if __name__=="__main__":
    unittest.main()
