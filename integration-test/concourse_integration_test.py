import unittest

from concourse_search.concourse import (
    ConcourseSearch,
)

class ConcourseIntegrationTest(unittest.TestCase):
    def test_it_returns_lines_from_a_concourse_build(self):
        lines = ConcourseSearch().find(
            target="gpdb-prod",
            job="gpdb_master/icw_planner_centos6",
            build=1
        )

        line_messages = [line.message() for line in lines]

        self.assertIn("real	60m28.873s\r\n", line_messages)

