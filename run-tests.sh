#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
# Copyright (C) 2019-2020 Northwestern University.
# Copyright (C) 2020-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

# Always bring down docker services

function cleanup() {
    eval "$(docker-services-cli down --env)"
}

# Check for arguments
# Note: "-k" would clash with "pytest"
keep_services=0
only_tests=0
pytest_args=()
for arg in $@; do
    # from the CLI args, filter out some known values and forward the rest to "pytest"
    # note: we don't use "getopts" here b/c of some limitations (e.g. long options),
    #       which means that we can't combine short options (e.g. "./run-tests -Kk pattern")
    case ${arg} in
	-K|--keep-services)
	    keep_services=1
	    ;;
        -O|--only-tests)
            only_tests=1
            ;;
	*)
	    pytest_args+=( ${arg} )
	    ;;
    esac
done

if [[ ${keep_services} -eq 0 ]]
then
    trap cleanup EXIT
fi

if [[ ${only_tests} -eq 0 ]]
then
    ruff check .

    python -m check_manifest
    python -m sphinx.cmd.build -qnNW docs docs/_build/html
fi
eval "$(docker-services-cli up --db ${DB:-postgresql} --search ${SEARCH:-opensearch} --env)"
python -m pytest ${pytest_args[@]+"${pytest_args[@]}"}
