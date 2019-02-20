import unittest
import re


from concourse_search.domain import (
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
            
