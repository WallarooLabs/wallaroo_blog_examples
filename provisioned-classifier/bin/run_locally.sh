#!/bin/sh
set -e
HOST=127.0.0.1
SINK_PORT=9999
SOURCE_PORT=8888
LEADER="$HOST"

stop_cluster_if_running() {
  cluster_shutdown "$HOST":5050 || true
}

clear_resilience(){
   rm -rf /tmp/classifier-*
}

stop_listener() {
  (ps aux | grep '[d]ata_receiver' | awk '{print $2}' | xargs -L1 kill -9) 2>/dev/null\
    || true
}

start_listener() {
  stop_listener
  nohup data_receiver  \
        --framed --listen "$LEADER":"$SINK_PORT" \
        --ponynopin \
        > "$OUTPUT" 2>&1 &
}

start_leader() {
  export PYTHONPATH="$PYTHONPATH:$WALLAROO_APP_DIR"
  nohup machida --application-module classifier \
          --in "$LEADER":"$SOURCE_PORT" \
          --out "$HOST":"$SINK_PORT" \
          --metrics "$LEADER":5001 \
          --control "$LEADER":12500 \
          --data "$LEADER":12600 \
          --external "$LEADER":5050 \
          --cluster-initializer \
          --worker-count $N_WORKERS \
          --ponynoblock --ponythreads=1 \
        > log/machida0.log 2>&1 &
}

start_worker() {
  N=$1
  export PYTHONPATH="$PYTHONPATH:$WALLAROO_APP_DIR"
  nohup machida --application-module classifier \
          --in "$HOST":$(($SOURCE_PORT+N)) \
          --out "$HOST":"$SINK_PORT" \
          --metrics "$LEADER":5001 \
          --control "$LEADER":12500 \
          --my-control "$HOST":$((12500+N)) \
          --my-data "$HOST":$((12600+N)) \
          --name "WORKER_$N" \
          --ponynoblock --ponythreads=1 \
        > log/machida$N.log 2>&1 &
}

start_cluster(){
  start_leader
  wait_for_port 5050
  for N in $(seq 1 $((N_WORKERS-1))); do start_worker $N; done
  wait_for_port "$SOURCE_PORT"
}

wait_for_port(){
  while !(nc -z "$LEADER" "$1") do
        sleep 0.1
        echo -n "z"
  done
}

send_data() {
  ./bin/send.py "$LEADER":"$SOURCE_PORT" --lines "$INPUT_LINES" &
}

wait_for_output(){
  OUTFILE="$OUTPUT"
  NEED=$(($INPUT_LINES - 1))
  GOT=$(wc -l "$OUTFILE" | awk '{print $1}')
  while [ "$GOT" != "$NEED" ] ; do
        GOT=$(wc -l "$OUTFILE" | awk '{print $1}') ;
  done
  echo "Got all $NEED lines of output."
}

stop_cluster_if_running
clear_resilience
start_listener
start_cluster
send_data
wait_for_output
stop_cluster_if_running
stop_listener
exit 0
