#!/bin/bash

DOCKERIZE_ARGS="-template /conf:/opt/janus/etc/janus su janus -c /opt/janus/bin/janus"
dockerize $DOCKERIZE_ARGS
