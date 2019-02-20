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
./bin/concourse-search find-failures --target some/target --job some_pipeline/some_job --build=[build number] --search='^SomeRegularExpression'
```

Prints out failures in the given build matching the regular expression.
