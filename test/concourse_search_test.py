import unittest
import re
import io


from concourse_search import (
    parse_args,
    display_failure_as_row
)

from concourse_search.domain import (
    Line
)


class ConcourseSearchTest(unittest.TestCase):
    def test_parse_args_determines_if_subcommand_is_legit(self):
        parsed_args = parse_args(["find-failures"])
        self.assertEqual(parsed_args.chosen_command().name(), 'find-failures')
        
    def test_parsed_args_includes_target(self):
        parsed_args = parse_args(["find-failures", "--target", "some/target"])
        command = parsed_args.chosen_command()
        self.assertEqual('some/target', command.target())
        
        parsed_args = parse_args(["find-failures", "--target", "some/other-target"])
        command = parsed_args.chosen_command()
        self.assertEqual('some/other-target', command.target())

    def test_parsed_args_includes_pipeline(self):
        parsed_args = parse_args(["find-failures", "--pipeline", "some/pipeline"])
        command = parsed_args.chosen_command()
        self.assertEqual('some/pipeline', command.pipeline())
        
        parsed_args = parse_args(["find-failures", "--pipeline", "some/other-pipeline"])
        command = parsed_args.chosen_command()
        self.assertEqual('some/other-pipeline', command.pipeline())

    def test_parsed_args_includes_job(self):
        parsed_args = parse_args(["find-failures", "--job", "some/job"])
        command = parsed_args.chosen_command()
        self.assertEqual('some/job', command.job())
        
        parsed_args = parse_args(["find-failures", "--job", "some/other-job"])
        command = parsed_args.chosen_command()
        self.assertEqual('some/other-job', command.job())

    def test_parsed_args_includes_build(self):
        parsed_args = parse_args(["find-failures", "--build", "456"])
        command = parsed_args.chosen_command()
        self.assertEqual(456, command.build())
        
        parsed_args = parse_args(["find-failures", "--build", '123'])
        command = parsed_args.chosen_command()
        self.assertEqual(123, command.build())

        
    def test_parsed_args_includes_search(self):
        parsed_args = parse_args(["find-failures", "--search", "some/search"])
        command = parsed_args.chosen_command()
        self.assertEqual('some/search', command.search().pattern)
        
        parsed_args = parse_args(["find-failures", "--search", "some/other-search"])
        command = parsed_args.chosen_command()
        self.assertEqual('some/other-search', command.search().pattern)

    def test_parsed_args_includes_verbose(self):
        parsed_args = parse_args(["--verbose", "find-failures"])
        command = parsed_args.chosen_command()
        self.assertTrue(command.verbose())
        
        parsed_args = parse_args(["find-failures"])
        command = parsed_args.chosen_command()
        self.assertFalse(command.verbose())

    def test_parsed_args_includes_limit(self):
        parsed_args = parse_args(["find-failures"])
        command = parsed_args.chosen_command()
        self.assertEqual(100, command.limit())
        
        parsed_args = parse_args(["find-failures", "--limit", "300"])
        command = parsed_args.chosen_command()
        self.assertEqual(300, command.limit())
        


def make_line(build_number=123,
              message="some message",
              target="some-target",
              job="some-job",
):
        return Line(
            message=message,
            build=build_number,
            target=target,
            job=job,
        )
    
class FailureDisplayTest(unittest.TestCase):
    def test_row_includes_build_number(self):
        failure = make_line(build_number=456)
        
        stdout = io.StringIO()
        
        display_failure_as_row(failure, stdout)

        stdout.seek(0)

        self.assertIn("456 |", stdout.read())

