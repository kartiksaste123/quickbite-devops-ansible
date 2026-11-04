# QuickBite - DevOps Case Study and Ansible Automation

Name: Kartik Saste
Subject: DevOps - Case Study & Ansible Automation Assignment (Internal Assessment 1)

## Project overview

For this assignment I picked a food delivery application called QuickBite. It is a small
order API where a customer can see the menu of a few restaurants and place an order.
The aim was not to build a big app but to show how a real food delivery system would move
through the DevOps lifecycle, and to automate the server setup with Ansible.

The app runs on three servers:

- web01 (webservers) - Nginx, works as reverse proxy in front of the app
- app01 (appservers) - QuickBite API written in Python Flask, runs with Gunicorn as a systemd service
- db01 (dbservers) - PostgreSQL 14 database that stores menu items and orders

All three servers also run Prometheus node_exporter on port 9100 so they can be monitored.
For the lab I used three Ubuntu 22.04 Docker containers (with systemd and SSH) as the
servers, so Ansible connects to them over SSH exactly like it would connect to VMs.

The lifecycle, architecture and CI/CD diagrams are in the `diagrams/` folder.

## Tech stack

| Stage | Tools |
|-------|-------|
| Plan | Jira |
| Code | Git, GitHub |
| Build | GitHub Actions (Jenkins can also be used), pip |
| Test | pytest, ansible-lint, ansible-playbook --syntax-check |
| Release | Git tags / GitHub Releases |
| Deploy | Ansible |
| Operate | Nginx, Gunicorn, systemd, PostgreSQL |
| Monitor | Prometheus node_exporter, Grafana, /health endpoint |

## Folder structure

```
devops-ansible-assignment/
├── ansible.cfg                 ansible settings (inventory path, become, ssh)
├── site.yml                    main playbook
├── requirements.yml            ansible collections used
├── inventory/
│   ├── hosts.ini               hosts and groups
│   ├── group_vars/             all.yml, webservers.yml, appservers.yml, dbservers.yml
│   └── host_vars/              web01.yml, app01.yml, db01.yml
├── roles/
│   ├── common/                 base packages, timezone, node_exporter, motd
│   ├── database/               postgresql install, config, db and user
│   ├── app/                    flask app, virtualenv, env file, systemd service
│   └── nginx/                  nginx install and reverse proxy site
├── tests/test_app.py           unit tests for the API
├── lab/                        Dockerfile + script to start the 3 test servers
├── .github/workflows/ci.yml    CI pipeline (lint, syntax check, tests)
├── diagrams/                   lifecycle, architecture and CI/CD diagrams
├── evidence/                   terminal output of every command I ran
├── screenshots/                screenshots of the same outputs
└── scripts/                    helper scripts used to save the outputs
```

## Prerequisites

- Linux machine (I used Debian) with Docker installed
- Python 3 and pip
- Ansible core 2.15 or newer (I used 2.21) and the collections in requirements.yml

```
python3 -m venv .venv
source .venv/bin/activate
pip install ansible ansible-lint
ansible-galaxy collection install -r requirements.yml
```

## How to run

1. Start the three servers. The script also creates an SSH key in `~/.ssh/quickbite/`
   (the private key stays there and is not part of this repo).

```
./lab/start_lab.sh
```

2. Check the inventory and connection

```
ansible-inventory --graph
ansible all -m ping
```

3. Check the playbook and run it

```
ansible-playbook site.yml --syntax-check
ansible-playbook site.yml
```

4. Open the app through nginx

```
curl http://127.0.0.1:8088/health
curl http://127.0.0.1:8088/api/menu
curl -X POST -H "Content-Type: application/json" \
     -d '{"customer": "Kartik", "item_id": 3, "qty": 2}' http://127.0.0.1:8088/api/orders
```

Only one part can also be run using tags, for example
`ansible-playbook site.yml --tags nginx` or `--tags verify`.

## Playbook details

`site.yml` has five plays: common setup on all hosts, database, app, nginx and at the end a
verify play which calls `/health` and `/api/menu` through nginx with the uri module and prints
the response.

Some points about the playbook:

- Roles are used so every tier is separate and can be reused for another project
- Templates (Jinja2) are used for the nginx site, the app env file, the systemd unit and motd
- Nginx upstream and pg_hba entries are built from the inventory groups, so adding a
  second app server only needs a new line in hosts.ini
- Handlers restart or reload a service only when its config actually changes
- The playbook is idempotent. The second run gives `changed=0` on all hosts
  (see `evidence/09_playbook_second_run_idempotent.txt`)
- Host specific values are in host_vars, for example app01 runs 3 gunicorn workers and
  db01 has max_connections set to 150

The database password is kept in group_vars only because this is a lab. In a real setup it
should be encrypted with ansible-vault.

## Evidence

| File | What it shows |
|------|---------------|
| 01_lab_containers | the three servers running |
| 02_ansible_version | ansible version and config file used |
| 03_inventory_graph | groups and hosts |
| 04_inventory_host_vars | variables merged for app01 |
| 05_ansible_ping | connection to all hosts |
| 06_syntax_check / 07_ansible_lint | playbook checks |
| 08_playbook_first_run | first run, everything installed and configured |
| 09_playbook_second_run_idempotent | second run with changed=0 |
| 10_curl_through_nginx | API working through nginx, order placed |
| 11_service_status | services active, node_exporter metrics |
| 12_run_with_tags | running only nginx and verify tags |
| 13_pytest | unit tests |
| 14_config_drift_fix | nginx site removed by hand, ansible puts it back |

Text output is in `evidence/` and the screenshots with the same name are in `screenshots/`.

## CI

`.github/workflows/ci.yml` runs on every push and pull request. It installs ansible,
runs the syntax check and ansible-lint, and then runs the pytest unit tests of the API.

## Cleanup

```
docker rm -f web01 app01 db01
```
