#!/bin/bash

set +e

export FULL_VERSION=`git describe --tags --abbrev=1`
export VERSION=${FULL_VERSION:1}

ansible-playbook deploy/deploy-indexer.yml \
                 -i deploy/inventories/production \
                 -l indexer
