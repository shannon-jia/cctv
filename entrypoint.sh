#!/bin/bash
set -e

if [ "$1" = 'sam-cctv' ]; then
    exec /app/sam-cctv
fi

exec "$@"
