#!/bin/bash -ex

drone exec --event push --pipeline static-tests .drone.yml
drone exec --event push --pipeline integration-test .drone.yml
