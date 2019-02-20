import unittest
import re


from concourse_search import (
    parse_args,
    FindFailuresCommand,
    Line,
)


class StubFindMessageCommand():
    def __init__(self):
        self._stubbed_rows = []
        
    def stub(self, stubbed_rows):
        self._stubbed_rows = stubbed_rows

    def find(self, target, job, build):
        return self._stubbed_rows.pop()
    

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
        parsed_args = parse_args(["find-failures", "--build", "some/build"])
        command = parsed_args.chosen_command()
        self.assertEqual('some/build', command.build())
        
        parsed_args = parse_args(["find-failures", "--build", "some/other-build"])
        command = parsed_args.chosen_command()
        self.assertEqual('some/other-build', command.build())

        
    def test_parsed_args_includes_search(self):
        parsed_args = parse_args(["find-failures", "--search", "some/search"])
        command = parsed_args.chosen_command()
        self.assertEqual('some/search', command.search())
        
        parsed_args = parse_args(["find-failures", "--search", "some/other-search"])
        command = parsed_args.chosen_command()
        self.assertEqual('some/other-search', command.search())



def make_line(message="some message"):
    return Line(
        message=message
        )


class FindFailuresTest(unittest.TestCase):
    def test_it_matches_lines_from_the_concourse_search(self):
        stub_find_message_command = StubFindMessageCommand()

        stub_find_message_command.stub([
            [
                make_line(message="some line with abc"),
                make_line(message="some line with def"),
                make_line(message="some line with ghi"),                
            ]
        ])
        
        command = FindFailuresCommand(stub_find_message_command)

        failures = command.find(
            target='some-target',
            build=1,
            job='some-job-name',
            search=re.compile('def')
        )

        failure_messages = [failure.message() for failure in failures]

        self.assertIn("some line with def", failure_messages)
        self.assertNotIn("some line with abc", failure_messages)
        self.assertNotIn("some line with ghi", failure_messages)
            
