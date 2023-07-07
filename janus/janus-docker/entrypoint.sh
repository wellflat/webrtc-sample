#!/bin/bash

DOCKERIZE_COMMON_ARGS="-template /conf:/opt/janus/etc/janus su app -c /opt/janus/bin/janus"
dockerize $DOCKERIZE_COMMON_ARGS