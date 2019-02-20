import unittest
import io
import tempfile


from concourse_search.cli import (
    main
)


class FindFailuresTest(unittest.TestCase):
    def test_find_failing_builds(self):
        fake_stdout = tempfile.TemporaryFile("rw+")

        main([
            "failing-builds",
            "--target", "gpdb-prod",
            "--pipeline", "gpdb_master",
            "--job", "icw_planner_centos6",
            "--starting-build", "10"
        ], stdout=fake_stdout)

        fake_stdout.seek(0)

        all_lines = fake_stdout.readlines()
        self.assertIn("9 | https://prod.ci.gpdb.pivotal.io/teams/main/pipelines/gpdb_master/jobs/icw_planner_centos6/builds/9 | /tmp/.concourse-search/gpdb-prod-gpdb-master-icw-planner-centos6-9.log\n", all_lines)
        self.assertIn("4 | https://prod.ci.gpdb.pivotal.io/teams/main/pipelines/gpdb_master/jobs/icw_planner_centos6/builds/4 | /tmp/.concourse-search/gpdb-prod-gpdb-master-icw-planner-centos6-4.log\n", all_lines)
        self.assertIn("3 | https://prod.ci.gpdb.pivotal.io/teams/main/pipelines/gpdb_master/jobs/icw_planner_centos6/builds/3 | /tmp/.concourse-search/gpdb-prod-gpdb-master-icw-planner-centos6-3.log\n", all_lines)
        self.assertIn("2 | https://prod.ci.gpdb.pivotal.io/teams/main/pipelines/gpdb_master/jobs/icw_planner_centos6/builds/2 | /tmp/.concourse-search/gpdb-prod-gpdb-master-icw-planner-centos6-2.log\n", all_lines)                
        self.assertNotIn("1 | https://prod.ci.gpdb.pivotal.io/teams/main/pipelines/gpdb_master/jobs/icw_planner_centos6/builds/1 | /tmp/.concourse-search/gpdb-prod-gpdb-master-icw-planner-centos6-1.log\n", all_lines)
        
