#!/usr/bin/env bash
# Creates 3 Ubuntu 22.04 containers that act as the managed nodes for this project.
#   web01 -> nginx       (ssh on localhost:2221, http on localhost:8088)
#   app01 -> flask api   (ssh on localhost:2222)
#   db01  -> postgresql  (ssh on localhost:2223)
# The containers run systemd so services behave like on a normal VM.
set -e
cd "$(dirname "$0")"

KEY_DIR="$HOME/.ssh/quickbite"
mkdir -p "$KEY_DIR"
if [ ! -f "$KEY_DIR/ansible_key" ]; then
  ssh-keygen -t ed25519 -N "" -C "ansible@quickbite-lab" -f "$KEY_DIR/ansible_key"
fi
cp "$KEY_DIR/ansible_key.pub" ./ansible_key.pub

docker build -t quickbite-node:22.04 .

start_node() {
  name=$1; ports=$2
  docker rm -f "$name" >/dev/null 2>&1 || true
  docker run -d --name "$name" --hostname "$name" $ports \
    --privileged --cgroupns=host -v /sys/fs/cgroup:/sys/fs/cgroup:rw \
    --tmpfs /run --tmpfs /run/lock \
    quickbite-node:22.04
}

start_node web01 "-p 2221:22 -p 8088:80"
start_node app01 "-p 2222:22"
start_node db01  "-p 2223:22"

docker ps --filter "ancestor=quickbite-node:22.04"
