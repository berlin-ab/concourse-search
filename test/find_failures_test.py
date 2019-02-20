import unittest
import re


from concourse_search.domain import (
    FindFailuresCommand,
    Line,
)


class StubFindMessageCommand():
    def __init__(self):
        self._stubbed_rows = []
        self.build_numbers_used = []
        
    def stub(self, stubbed_rows):
        self._stubbed_rows = stubbed_rows

    def find(self, target, pipeline, job, build):
        self.build_numbers_used.append(build)

        if self._stubbed_rows:
            return self._stubbed_rows.pop()

        return []
    

def make_line(
        message="some message",
        pipeline="some-pipeline",
        job="some-job",
        target="some-target",
        build=123):
    return Line(
        message=message,
        pipeline=pipeline,
        job=job,
        target=target,
        build=build,
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
            pipeline='some-pipeline-name',
            build=1,
            job='some-job-name',
            search=re.compile('def')
        )

        failure_messages = [failure.message() for failure in failures]

        self.assertIn("some line with def", failure_messages)
        self.assertNotIn("some line with abc", failure_messages)
        self.assertNotIn("some line with ghi", failure_messages)

    def test_it_asks_for_all_of_the_builds_lower_than_the_build_number(self):
        stub_find_message_command = StubFindMessageCommand()
        command = FindFailuresCommand(stub_find_message_command)

        command.find(
            target='some-target',
            pipeline='some-pipeline-name',
            build=2,
            job='some-job-name',
            search=re.compile('def')
        )


        self.assertIn(1, stub_find_message_command.build_numbers_used)
        self.assertIn(2, stub_find_message_command.build_numbers_used)
        
    def test_it_only_looks_back_n_number_of_builds(self):
        stub_find_message_command = StubFindMessageCommand()
        command = FindFailuresCommand(stub_find_message_command)

        command.find(
            target='some-target',
            pipeline='some-pipeline-name',
            build=5,
            job='some-job-name',
            search=re.compile('def'),
            limit=2
        )

        self.assertIn(5, stub_find_message_command.build_numbers_used)
        self.assertIn(4, stub_find_message_command.build_numbers_used)
        self.assertNotIn(3, stub_find_message_command.build_numbers_used)
        self.assertNotIn(2, stub_find_message_command.build_numbers_used)
        self.assertNotIn(1, stub_find_message_command.build_numbers_used)

