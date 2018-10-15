#!/bin/sh
# TODO: use `pulumi stack output X` syntax
#set -x

make_line() {
    MACHINE_TYPE="$1"
    echo "$STACK" \
	| grep "$MACHINE_TYPE" \
	| awk '{print $2}' \
	| jq '.[] | [.publicDns, .privateIp]' \
	| jq -r '.[0] + " ansible_user=ubuntu private_ip=" + .[1]'
}

STACK=$(pulumi stack output | tail -n+3)

echo "[metrics_host]"
echo "$(make_line metrics_host)"

echo "\n[initializer]"
echo "$(make_line initializer)"

echo "\n[workers]"
for line in "$(make_line workers)"; do echo "$line"; done
