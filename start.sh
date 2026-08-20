#!/bin/sh

set -e

echo "Starting Fraud Radar on port ${PORT:-10000}..."

exec reflex run --env prod --frontend-port "${PORT:-10000}"