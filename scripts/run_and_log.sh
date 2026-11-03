#!/usr/bin/env bash
# Usage: scripts/run_and_log.sh <name> "<command 1>" ["<command 2>" ...]
# Runs each command, shows it like a terminal session and saves everything to evidence/<name>.txt
set -o pipefail
name="$1"; shift
for cmd in "$@"; do
  echo "kartik@devops-lab:~/devops-ansible-assignment\$ ${cmd}"
  bash -c "${cmd}" 2>&1
done | tee "evidence/${name}.txt"
