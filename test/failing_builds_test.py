import unittest


from concourse_search.domain import (
    FailingBuildsCommand,
    Build,
)


class StubConcourseSearch():

    def __init__(self):
        self._stubbed_return_values = []
        self.used_target = None
        self.used_pipeline = None
        self.used_job = None
        self.used_starting_build_number = None
        self.used_limit = None
        
    def stub(self, stubbed_return_values):
        self._stubbed_return_values = stubbed_return_values

    def find_builds(self, target, pipeline, job, starting_build_number, limit):
        self.used_target = target
        self.used_pipeline = pipeline
        self.used_job = job
        self.used_starting_build_number = starting_build_number
        self.used_limit = limit
        return self._stubbed_return_values
    

def make_build(number=111, failing=False):
    return Build(
        number=number,
        failing=failing,
        pipeline='some-pipeline',
        job='some-job',
        base_url='http://example.com',
        logfile_path='/tmp/some-logfile-path.log',
    )


class FailingBuildsTest(unittest.TestCase):
    def setUp(self):
        self.concourse_search = StubConcourseSearch()
        self.failing_builds_command = FailingBuildsCommand(
            self.concourse_search
        )
        
    def test_it_returns_a_list_of_builds_that_failed_for_a_given_job(self):
        self.concourse_search.stub([
            make_build(number=123, failing=False),
            make_build(number=456, failing=True),
            make_build(number=789, failing=False),
        ])
        
        builds = self.failing_builds_command.find(
            target='here',
            pipeline='soemthing',
            job='asdfas',
            starting_build_number=1,
            limit=123,
        )
        failing_build_numbers = [build.number() for build in builds]
        self.assertIn(456, failing_build_numbers)
        self.assertNotIn(123, failing_build_numbers)
        self.assertNotIn(789, failing_build_numbers)

    def test_it_receives_the_given_build_parameters(self):
        builds = self.failing_builds_command.find(
            target="some-target",
            pipeline='some-pipeline',
            job='some-job',
            starting_build_number=123,
            limit=1000,
        )
        
        self.assertEqual('some-target', self.concourse_search.used_target)
        self.assertEqual('some-pipeline', self.concourse_search.used_pipeline)
        self.assertEqual('some-job', self.concourse_search.used_job)
        self.assertEqual(123, self.concourse_search.used_starting_build_number)
        self.assertEqual(1000, self.concourse_search.used_limit)

