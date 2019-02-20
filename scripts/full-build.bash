#!/usr/bin/env bash

set -e

pyenv local 2.7.15
python --version

./scripts/build.bash

pyenv local 3.6.8
python --version

./scripts/build.bash
