#!/bin/bash
#
# Start InfluxDB, Grafana, and run main.py.

set -euo pipefail

set -a
source .env
set +a

# Run InfluxDB in background
influxdb3 &
INFLUX_PID=$!

# Kill InfluxDB upon script exit
trap "kill "$INFLUX_PID" 2>/dev/null || true" EXIT

# Start Grafana if not already started
if ! brew services list | grep -q "grafana.*started"; then
  brew services start grafana
fi

# Poll InfluxDB until it starts up
until curl -fsS \
  -H "Authorization: Bearer $INFLUXDB_TOKEN" \
  http://localhost:8181/health >/dev/null; do
  sleep 1
done

# Subscribe to MQTT broker and write data if need
source .venv/bin/activate
python main.py
