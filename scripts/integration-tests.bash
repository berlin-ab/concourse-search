#!/usr/bin/env bash

find . -name *.pyc | xargs --no-run-if-empty rm

nosetests -s --rednose integration-test/*.py
