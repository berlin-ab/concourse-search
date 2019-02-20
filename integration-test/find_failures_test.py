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
            "--job", "gpdb_master/icw_planner_centos6",
            "--build", "1537",
            "--search", "^\+Fatal Python error: GC\s.*$"
        ], stdout=fake_stdout)

        fake_stdout.seek(0)

        all_lines = fake_stdout.readlines()
        self.assertIn("+Fatal Python error: GC object already tracked\r\n", all_lines)
        self.assertNotIn(" TODAYS_DATE1|INFO|gpload session started TODAYS_DATE2\r\n", all_lines)
