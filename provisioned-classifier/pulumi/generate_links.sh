#!/bin/sh
STACK=$(pulumi stack output | tail -n+3)

echo "\nMetrics Host URL:"
echo "$STACK" \
  | grep metrics_host \
  | awk '{print $2}' \
  | jq '.[] | [.publicDns]' \
  | jq -r '.[0]' \
  | xargs -I% echo http://%:4000

echo "\nCloudwatch dashboard URL:"
echo "$STACK" \
  | grep dashboard \
  | awk '{print $2}'

echo


