# Concourse Search

Spelunk through Concourse CI build logs

## Getting Started

### Installation:

* download the `fly` utility from concourse and ensure it is in your PATH
* Download the project:

```
git clone https://github.com/berlin-ab/concourse-search.git
cd concourse-search;
```

### Usage:

```
./bin/concourse-search find-failures --target [some-target] --pipeline [some-pipeline] --job [some-job] --build=[build number] --search='^SomeRegularExpression'
```

Prints out failures in the given build matching the regular expression.


### Commands:

#### *find-failures*

Find all occurrences of a failure in a job.

#### *failing-builds*

Find all of the failing builds for a job.

### Developers

#### Install test dependencies:

```
pip install -r requirements-development.txt
```

#### Run unit tests:

./scripts/unit-tests.bash

#### Run integration tests:

./scripts/integration-tests.bash

#### Run feature tests:

./scripts/feature-tests.bash

#### Run everything:

./scripts/full-build.bash
