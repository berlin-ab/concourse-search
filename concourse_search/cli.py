import sys

import argparse


from concourse_search.components import (
    Components,
    FindFailuresArguments,
    FailingBuildsArguments,
)


def add_target_argument(parser):
    parser.add_argument('--target', required=True)

    
def add_pipeline_argument(parser):
    parser.add_argument('--pipeline', required=True)


def add_job_argument(parser):
    parser.add_argument('--job', required=True)

    
def find_failures_subparser(subparsers):
    subparser = subparsers.add_parser('find-failures')
    add_target_argument(subparser)
    add_pipeline_argument(subparser)
    add_job_argument(subparser)

    subparser.add_argument('--build', type=int, required=True)
    subparser.add_argument('--search', required=True)
    subparser.add_argument('--limit', default=100, type=int)

    
def failing_builds_subparser(subparsers):
    subparser = subparsers.add_parser('failing-builds')
    add_target_argument(subparser)
    add_pipeline_argument(subparser)
    add_job_argument(subparser)
    subparser.add_argument('--starting-build', type=int, required=True)


def parse_args(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action='store_true', default=False)
    
    subparsers = parser.add_subparsers(dest="chosen_command")
    find_failures_subparser(subparsers)
    failing_builds_subparser(subparsers)
    
    args = parser.parse_args(arguments)

    if args.chosen_command == 'find-failures':
        return FindFailuresArguments(args)
    elif args.chosen_command == 'failing-builds':
        return FailingBuildsArguments(args)
    else:
        print("Unknown command")
        exit(1)

    
def display_failure_as_row(failure, stdout):
    stdout.write(u"{build_number} | {url} | {message}".format(
        build_number=failure.build(),
        url=failure.url(),
        message=failure.message().decode('utf-8')
    ))
    
        
def display_build_as_row(build, stdout):
    stdout.write(u"{build_number} | {url}\n".format(
        build_number=build.number(),
        url=build.url(),
    ))
    
        
def find_failures_runner(components, arguments):
    for failure in components.find_failures().find(
        target=arguments.target(),
        build=arguments.build(),
        pipeline=arguments.pipeline(),
        job=arguments.job(),
        search=arguments.search(),
        limit=arguments.limit(),
    ):
        display_failure_as_row(failure, components.stdout())

        
def failing_builds_runner(components, arguments):
    for build in components.failing_builds().find(
        target=arguments.target(),
        starting_build_number=arguments.starting_build(),
        pipeline=arguments.pipeline(),
        job=arguments.job(),
    ):
        display_build_as_row(build, components.stdout())

    
def main(arguments, stdout=sys.stdout):
    runners = {
        'find-failures': find_failures_runner,
        'failing-builds': failing_builds_runner,
    }
    
    parsed_arguments = parse_args(arguments)
    components = Components(stdout, parsed_arguments.verbose())
    runner = runners[parsed_arguments.chosen_command().name()]

    if runner:
        runner(components, parsed_arguments)
    else:
        print("Unknown command")
        
