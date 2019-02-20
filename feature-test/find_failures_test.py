import unittest
import io
import tempfile


from concourse_search import main


class FindFailuresTest(unittest.TestCase):
    def test_find_failures(self):
        fake_stdout = tempfile.TemporaryFile("rw+")

        main([
            "find-failures",
            "--target", "gpdb-prod",
            "--pipeline", "gpdb_master",
            "--job", "icw_planner_centos6",
            "--build", "2",
            "--search", "^test replication_views_mirrored\s*\.\.\.\s*FAILED"
        ], stdout=fake_stdout)

        fake_stdout.seek(0)

        all_lines = fake_stdout.readlines()
        self.assertIn("2 | test replication_views_mirrored ... FAILED\r\n", all_lines)
        self.assertNotIn("2 | server stopped\r\n", all_lines)
