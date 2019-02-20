import sys

import argparse


from concourse_search.components import (
    Components,
    FindFailuresArguments,
)


def find_failures_subparser(subparsers):
    find_failures_parser = subparsers.add_parser('find-failures')
    find_failures_parser.add_argument('--target', required=True)
    find_failures_parser.add_argument('--pipeline', required=True)
    find_failures_parser.add_argument('--job', required=True)
    find_failures_parser.add_argument('--build', type=int, required=True)
    find_failures_parser.add_argument('--search', required=True)
    find_failures_parser.add_argument('--limit', default=100, type=int)

    
def parse_args(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action='store_true', default=False)
    
    subparsers = parser.add_subparsers(dest="chosen_command")
    find_failures_subparser(subparsers)
    args = parser.parse_args(arguments)

    if args.chosen_command == 'find-failures':
        return FindFailuresArguments(args)
    else:
        print("Unknown command")
        exit(1)

    
def display_failure_as_row(failure, stdout):
    stdout.write(u"{build_number} | {url} | {message}".format(
        build_number=failure.build(),
        url=failure.url(),
        message=failure.message().decode('utf-8')
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
    
    
def main(arguments, stdout=sys.stdout):
    runners = {
        'find-failures': find_failures_runner
    }
    
    parsed_arguments = parse_args(arguments)
    components = Components(stdout, parsed_arguments.verbose())
    runner = runners[parsed_arguments.chosen_command().name()]

    if runner:
        runner(components, parsed_arguments)
    else:
        print("Unknown command")
        
