#!/bin/sh

#!/bin/sh

# When run from inside a tmux window, this script:
# - opens two tmux panes logged in to the intializer machine
# - for every worker machine, opens a tmux pane logged in to
#   that machine

if ! [ -f "./ssh_key.pem" ]; then
    echo "./ssh_key.pem missing" >&2
    exit 1
fi

inventory=ansible/inventory.yml
initializer=$(grep -a1 initializer "$inventory"  | tail -n+2 | awk '{print $1}')
metrics_host=$(grep -a1 metrics_host "$inventory"  | tail -n+2 | awk '{print $1}')
workers=$(cat "$inventory" | awk 'p; /workers/{p=1}' | awk '{print $1}')

for host in $metrics_host $initializer $workers; do
  tmux split-window "ssh ubuntu@${host} -i ./ssh_key.pem";
  tmux select-layout even-horizontal
done

# close this window if tmux commands were successful
if [ "0" = "$?" ] ; then exit 0; fi


