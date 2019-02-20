import unittest


from concourse_search.concourse import (
    ConcourseSearch,
)


class ConcourseIntegrationTest(unittest.TestCase):
    def test_it_returns_lines_from_a_concourse_build(self):
        lines = ConcourseSearch().find(
            target="gpdb-prod",
            pipeline="gpdb_master",
            job="icw_planner_centos6",
            build=1
        )

        line_messages = [line.message() for line in lines]

        self.assertIn("real	60m28.873s\r\n", line_messages)

        line = lines[0]
        self.assertEqual(line.pipeline(), "gpdb_master")
        self.assertEqual(line.job(), "icw_planner_centos6")
        self.assertEqual(line.target(), "gpdb-prod")
        self.assertEqual(line.build(), 1)

    def test_it_returns_line_information_after_caching(self):
        ConcourseSearch().find(
            target="gpdb-prod",
            pipeline="gpdb_master",
            job="icw_planner_centos6",
            build=1
        )
        
        lines = ConcourseSearch().find(
            target="gpdb-prod",
            pipeline="gpdb_master",
            job="icw_planner_centos6",
            build=1
        )

        line = lines[0]
        self.assertEqual(line.pipeline(), "gpdb_master")
        self.assertEqual(line.job(), "icw_planner_centos6")
        self.assertEqual(line.target(), "gpdb-prod")
        self.assertEqual(line.build(), 1)
        
    def test_it_stores_download_in_a_local_cache(self):
        lines = ConcourseSearch().find(
            target="gpdb-prod",
            pipeline="gpdb_master",
            job="icw_planner_centos6",
            build=1
        )
        
        log_filename = "/tmp/.concourse-search/gpdb-prod-gpdb-master-icw-planner-centos6-1.log"
        
        with open(log_filename, "r") as file:
            self.assertIn("real	60m28.873s\r\n", file.readlines())
