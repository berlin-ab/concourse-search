import unittest


from concourse_search.concourse import (
    ConcourseSearch,
)

from concourse_search.fly import (
    FlyViaCli,
)

class ConcourseIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.concourse_search = ConcourseSearch(fly=FlyViaCli())
        
    def test_it_returns_lines_from_a_concourse_build(self):
        lines = self.concourse_search.find(
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
        self.concourse_search.find(
            target="gpdb-prod",
            pipeline="gpdb_master",
            job="icw_planner_centos6",
            build=1
        )
        
        lines = self.concourse_search.find(
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
        lines = self.concourse_search.find(
            target="gpdb-prod",
            pipeline="gpdb_master",
            job="icw_planner_centos6",
            build=1
        )
        
        log_filename = "/tmp/.concourse-search/gpdb-prod-gpdb-master-icw-planner-centos6-1.log"
        
        with open(log_filename, "r") as file:
            self.assertIn("real	60m28.873s\r\n", file.readlines())

    def test_it_returns_a_url_for_the_build_the_line_was_extracted_from(self):
        lines = self.concourse_search.find(
            target="gpdb-prod",
            pipeline="gpdb_master",
            job="icw_planner_centos6",
            build=1
        )

        line = lines[0]

        self.assertEqual("https://prod.ci.gpdb.pivotal.io/teams/main/pipelines/gpdb_master/jobs/icw_planner_centos6/builds/1", line.url())

    def test_it_returns_all_builds(self):
        builds = self.concourse_search.find_builds(
            target="gpdb-prod",
            pipeline="gpdb_master",
            job="icw_planner_centos6",
            starting_build_number=10
        )

        build_numbers = [build.number() for build in builds]
        self.assertEqual([10, 9, 8, 7, 6, 5, 4, 3, 2, 1], build_numbers)

    def test_it_limits_the_number_of_returned_builds(self):
        builds = self.concourse_search.find_builds(
            target="gpdb-prod",
            pipeline="gpdb_master",
            job="icw_planner_centos6",
            starting_build_number=10,
            limit=2,
        )

        build_numbers = [build.number() for build in builds]
        self.assertEqual([10, 9], build_numbers)

