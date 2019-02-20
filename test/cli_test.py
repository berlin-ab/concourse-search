import unittest
import re
import io


from concourse_search.cli import (
    parse_args,
    display_failure_as_row
)

from concourse_search.domain import (
    Line
)


def find_failures_arguments(subcommand='find-failures',
                            target='some-target',
                            pipeline='some-pipeline',
                            job='some-job',
                            build='123',
                            search="some search",
                            limit=None,
):
    arguments = []

    if subcommand: arguments.append(subcommand)
    if target: arguments.extend(["--target", target])
    if pipeline: arguments.extend(["--pipeline", pipeline])
    if job: arguments.extend(["--job", job])
    if search: arguments.extend(["--search", search])
    if build: arguments.extend(["--build", build])
    if limit: arguments.extend(["--limit", limit])

    return arguments


def failing_builds_arguments(subcommand='failing-builds',
                             target='some-target',
                             pipeline='some-pipeline',
                             job='some-job',
                             starting_build='111',
                             limit=None,
):
    arguments = []

    if subcommand: arguments.append(subcommand)
    if target: arguments.extend(["--target", target])
    if pipeline: arguments.extend(["--pipeline", pipeline])
    if job: arguments.extend(['--job', job])
    if starting_build: arguments.extend(['--starting-build', starting_build])
    if limit: arguments.extend(['--limit', limit])

    return arguments


class FailingBuildsCliTest(unittest.TestCase):

    def test_parse_args_determines_if_subcommand_is_legit(self):
        parsed_args = parse_args(failing_builds_arguments(subcommand="failing-builds"))
        self.assertEqual(parsed_args.chosen_command().name(), 'failing-builds')

    def test_parse_args_takes_target_parameter(self):
        parsed_args = parse_args(failing_builds_arguments(target='this-target'))
        self.assertEqual(parsed_args.target(), 'this-target')

    def test_parse_args_takes_pipeline_parameter(self):
        parsed_args = parse_args(failing_builds_arguments(pipeline='this-pipeline'))
        self.assertEqual(parsed_args.pipeline(), 'this-pipeline')

    def test_parse_args_takes_job_parameter(self):
        parsed_args = parse_args(failing_builds_arguments(job='this-job'))
        self.assertEqual(parsed_args.job(), 'this-job')

    def test_parse_args_takes_starting_build_parameter(self):
        parsed_args = parse_args(failing_builds_arguments(starting_build='999'))
        self.assertEqual(parsed_args.starting_build(), 999)

    def test_parse_args_takes_limit_parameter(self):
        parsed_args = parse_args(failing_builds_arguments(limit='99'))
        self.assertEqual(parsed_args.limit(), 99)

    def test_parse_args_defaults_limit_parameter(self):
        parsed_args = parse_args(failing_builds_arguments(limit=None))
        self.assertEqual(parsed_args.limit(), 100)

    def test_it_takes_a_verbose_argument(self):
        arguments = []
        arguments.append("--verbose")
        arguments.extend(failing_builds_arguments())
        
        parsed_args = parse_args(arguments)
        self.assertEqual(parsed_args.verbose(), True)
        

class FindFailuresCliTest(unittest.TestCase):
    def test_parse_args_determines_if_subcommand_is_legit(self):
        parsed_args = parse_args(find_failures_arguments(subcommand="find-failures"))
        self.assertEqual(parsed_args.chosen_command().name(), 'find-failures')

    def test_parsed_args_includes_target(self):
        parsed_args = parse_args(find_failures_arguments(target="some/target"))
        command = parsed_args.chosen_command()
        self.assertEqual('some/target', command.target())
        
        parsed_args = parse_args(find_failures_arguments(target="some/other-target"))
        command = parsed_args.chosen_command()
        self.assertEqual('some/other-target', command.target())

    def test_parsed_args_includes_pipeline(self):
        parsed_args = parse_args(find_failures_arguments(pipeline="some/pipeline"))
        command = parsed_args.chosen_command()
        self.assertEqual('some/pipeline', command.pipeline())
        
        parsed_args = parse_args(find_failures_arguments(pipeline="some/other-pipeline"))
        command = parsed_args.chosen_command()
        self.assertEqual('some/other-pipeline', command.pipeline())

    def test_parsed_args_includes_job(self):
        parsed_args = parse_args(find_failures_arguments(job="some/job"))
        command = parsed_args.chosen_command()
        self.assertEqual('some/job', command.job())
        
        parsed_args = parse_args(find_failures_arguments(job="some/other-job"))
        command = parsed_args.chosen_command()
        self.assertEqual('some/other-job', command.job())

    def test_parsed_args_includes_build(self):
        parsed_args = parse_args(find_failures_arguments(build="456"))
        command = parsed_args.chosen_command()
        self.assertEqual(456, command.build())
        
        parsed_args = parse_args(find_failures_arguments(build='123'))
        command = parsed_args.chosen_command()
        self.assertEqual(123, command.build())

    def test_parsed_args_includes_search(self):
        parsed_args = parse_args(find_failures_arguments(search="some/search"))
        command = parsed_args.chosen_command()
        self.assertEqual('some/search', command.search().pattern)
        
        parsed_args = parse_args(find_failures_arguments(search="some/other-search"))
        command = parsed_args.chosen_command()
        self.assertEqual('some/other-search', command.search().pattern)

    def test_parsed_args_includes_verbose(self):
        arguments = []
        arguments.append("--verbose")
        arguments.extend(find_failures_arguments())
        
        parsed_args = parse_args(arguments)
        command = parsed_args.chosen_command()
        self.assertTrue(command.verbose())
        
        parsed_args = parse_args(find_failures_arguments())
        command = parsed_args.chosen_command()
        self.assertFalse(command.verbose())

    def test_parsed_args_includes_limit(self):
        parsed_args = parse_args(find_failures_arguments())
        command = parsed_args.chosen_command()
        self.assertEqual(100, command.limit())
        
        parsed_args = parse_args(find_failures_arguments(limit="300"))
        command = parsed_args.chosen_command()
        self.assertEqual(300, command.limit())
        


def make_line(build_number=123,
              message="some message",
              target="some-target",
              pipeline="some-pipeline",
              job="some-job",
              base_url="http://example.com",
):
        return Line(
            message=message,
            target=target,
            pipeline=pipeline,
            build=build_number,
            job=job,
            base_url=base_url,
        )

    
class FailureDisplayTest(unittest.TestCase):
    def test_row_includes_build_number(self):
        failure = make_line(build_number=456)
        
        stdout = io.StringIO()
        
        display_failure_as_row(failure, stdout)

        stdout.seek(0)

        self.assertIn("456 |", stdout.read())

    def test_row_includes_url(self):
        failure = make_line(
            build_number=456,
            base_url='http://example.com/some-base-url',
            job='some-job',
            pipeline='some-pipeline'
        )

        stdout = io.StringIO()

        display_failure_as_row(failure, stdout)

        stdout.seek(0)

        self.assertIn("| http://example.com/some-base-url/teams/main/pipelines/some-pipeline/jobs/some-job/builds/456", stdout.read())

