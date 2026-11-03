# QuickBite Demo Script (about 6 minutes)

Kartik Saste - DevOps Case Study and Ansible Automation

Speak normally, not too fast. The lines under "Say" are a guide; you do not have to read them word for word. The lines under "Type" are the exact commands, in order.

---

## Pre-recording checklist

Do all of this before pressing record.

1. Docker is running on the machine.
2. Open a terminal in the project folder and start fresh servers, so the first playbook run really shows changes:

   ```
   cd ~/devops-ansible-assignment
   ./lab/start_lab.sh
   ```

3. Activate the virtual environment and make sure the collections are installed:

   ```
   source .venv/bin/activate
   ansible-galaxy collection install -r requirements.yml
   ```

4. Quick check that SSH works (then clear the screen):

   ```
   ansible all -m ping
   clear
   ```

5. Open these in VS Code (or any editor) as tabs, in this order: `diagrams/devops_lifecycle.png`, `diagrams/architecture.png`, `diagrams/ci_cd_workflow.png`, `inventory/hosts.ini`, `inventory/group_vars/all.yml`, `inventory/host_vars/app01.yml`, `site.yml`, `roles/database/tasks/main.yml`, `roles/nginx/templates/quickbite.conf.j2`, `roles/app/handlers/main.yml`.
6. Make the terminal font big (at least 16 pt) and the window wide, so the PLAY RECAP line does not wrap.
7. Turn off notifications. Close other browser tabs.
8. The first playbook run installs packages and can take a few minutes. Plan to pause the recording (or cut it in editing) while it runs, and resume when the PLAY RECAP shows. Say this in the video so it does not look like a hidden edit.
9. Note: on fresh servers, the order you place in the demo will be `order_id 1`, not 2 as in my evidence file. That is normal.
10. Keep the demo between 5 and 7 minutes. Do one practice run.

---

## 0:00 - 0:45  Introduction and scenario

Show: README.md or the title page of the report.

Say:

> Hi, I am Kartik Saste, and this is my demo for the DevOps case study and Ansible automation assignment.
> For the scenario, I picked a food delivery system. I use apps like Swiggy and Zomato a lot, and they are a good DevOps example because they have big lunch and dinner peaks, and the menus change all the time, so they need frequent but safe releases.
> I made a small order API called QuickBite. It is written in Flask and has a menu endpoint, an orders endpoint, and a health check.
> It runs on three servers: web01 with Nginx, app01 with the Flask app under Gunicorn, and db01 with PostgreSQL 14. For the lab, these are three Ubuntu 22.04 Docker containers that Ansible reaches over SSH, just like normal VMs.

---

## 0:45 - 1:30  Lifecycle, architecture, and CI/CD diagrams

Show: `diagrams/devops_lifecycle.png`, then `architecture.png`, then `ci_cd_workflow.png`.

Say:

> This is the DevOps lifecycle I designed. Plan in Jira, code in Git and GitHub, build and test in GitHub Actions with pytest, ansible-lint, and the syntax check, release with Git tags, deploy with my Ansible playbook, operate with Nginx, Gunicorn, systemd, and PostgreSQL, and monitor with node_exporter, Prometheus, and Grafana. The dashed arrow shows that problems from monitoring go back into planning.
>
> (architecture) A customer request goes to Nginx on web01, Nginx proxies it to Gunicorn on app01, port 5000, and the app talks to PostgreSQL on db01. Every server runs node_exporter on port 9100. On the side is my Ansible control node, which connects to all three over SSH.
>
> (CI/CD) And this is the workflow. A pull request triggers GitHub Actions. If lint, the syntax check, and the tests pass, it is merged and tagged. Then the playbook runs on staging, the verify play checks the app, and the same playbook can go to production with a different inventory.

---

## 1:30 - 2:15  Inventory walkthrough

Show: `inventory/hosts.ini`, then `group_vars/all.yml`, then `host_vars/app01.yml`.

Say:

> This is my inventory. I have three groups: webservers, appservers, and dbservers, with one host in each. They all use 127.0.0.1 with different SSH ports, 2221 to 2223, because they are containers on my machine. foodapp is a parent group made with children, so I can target the whole application at once, and its vars set the environment to staging.
> Common variables like the SSH user, the ports, and the database details are in group_vars/all.yml. Host vars override group vars. For example, appservers has 2 Gunicorn workers, but app01 has 3 in its host_vars.

Type:

```
ansible-inventory --graph
ansible-inventory --host app01 --yaml
ansible all -m ping
```

Say (pointing at the output):

> The graph shows foodapp with the three groups. For app01, the final value of gunicorn_workers is 3, so the host variable won. And ping gets a pong from all three servers.

---

## 2:15 - 3:00  Playbook and roles

Show: `site.yml`, then `roles/database/tasks/main.yml` (the pg_hba task and flush_handlers), `roles/nginx/templates/quickbite.conf.j2` (the upstream loop), `roles/app/handlers/main.yml`.

Say:

> site.yml has five plays: common on all servers, then the database, then the app, then Nginx, and at the end a verify play that calls the health and menu endpoints through Nginx. Each role has a tag, so I can run just one part.
> I used four roles: common, database, app, and nginx, so each tier is separate and reusable.
> In the database role, the pg_hba rule loops over the appservers group, so a new app server is allowed automatically. I flush handlers here, so PostgreSQL restarts before the app play starts.
> In the Nginx template, the upstream is also built from the appservers group.
> And these are the handlers. A service is restarted or reloaded only when its config file actually changes.

---

## 3:00 - 4:00  Checks and the first run

Type:

```
ansible-playbook site.yml --syntax-check
ansible-lint
python -m pytest -v tests/
ansible-playbook site.yml
```

Say (while the checks run):

> First, the same checks that CI runs. The syntax check passes. ansible-lint passes with 0 failures on the production profile. And both unit tests pass.
> Now the real run on fresh servers.

(Pause the recording while the packages install. Resume when the PLAY RECAP is on screen.)

Say:

> I paused the recording while packages were installing. Here is the result. Most tasks are yellow, changed, because the servers were empty. The verify play shows the database is up and the menu returned 5 items. In the recap, app01, db01, and web01 all have failed equal to 0 and unreachable equal to 0.
> (In my evidence run, it was app01 ok 18 changed 13, db01 ok 14 changed 11, web01 ok 19 changed 11.)
> If you see a deprecation warning about INJECT_FACTS_AS_VARS, it is only a warning about my private_ip variable for a future Ansible version. It does not affect the run.

---

## 4:00 - 4:30  Second run (idempotency)

Type:

```
ansible-playbook site.yml
```

Say:

> Now I run exactly the same command again without changing anything. Everything is green, and the recap shows changed equal to 0 on all three hosts. The ok counts are a bit lower because no handlers ran. This is idempotency. The playbook only changes what is not already in the right state, so it is safe to run again and again.

---

## 4:30 - 5:05  Testing the app through Nginx and checking services

Type:

```
curl -s http://127.0.0.1:8088/; echo
curl -s http://127.0.0.1:8088/health; echo
curl -s http://127.0.0.1:8088/api/menu | python3 -m json.tool
curl -s -X POST -H 'Content-Type: application/json' -d '{"customer": "Kartik", "item_id": 3, "qty": 2}' http://127.0.0.1:8088/api/orders; echo
curl -s http://127.0.0.1:8088/api/orders; echo
ansible appservers -a "systemctl is-active quickbite"
ansible foodapp -m shell -a "curl -s localhost:9100/metrics | grep -c ^node_"
```

Say:

> All these requests go through Nginx on port 8088. served_by says app01, so Nginx is forwarding to the app server, and env is staging from the template. Health says the database is up. The menu comes from PostgreSQL, and I just placed an order for two plates of Chicken Biryani, which returned status PLACED, and it shows up in the orders list.
> The quickbite service is active, and node_exporter returns over a thousand metrics on every server, ready for Prometheus.

(Optional if time allows: `ansible webservers -a "systemctl is-active nginx"` and `ansible dbservers -a "systemctl is-active postgresql"`.)

---

## 5:05 - 5:40  Configuration drift fix

Type:

```
ansible webservers -m file -a "path=/etc/nginx/sites-enabled/quickbite.conf state=absent"
ansible-playbook site.yml --tags nginx,verify
```

Say:

> Now I break something on purpose, like someone making a wrong manual change. I delete the QuickBite site link from Nginx on web01.
> Then I run only the nginx and verify parts with tags. Ansible notices the link is missing, the "Enable QuickBite site" task shows changed, the handler reloads Nginx, and verify confirms the app works again. The recap shows web01 changed equal to 2, and app01 and db01 were not touched.

---

## 5:40 - 6:00  Wrap-up

Show: the GitHub repository page (Actions tab if the CI run is green).

Say:

> To sum up, I designed the full DevOps lifecycle for a food delivery app, prepared an inventory with groups, a parent group, and host variables, and wrote a role-based playbook that sets up the database, the app, and Nginx in one command, is idempotent, and fixes drift. Everything, including the evidence and the screenshots, is in my GitHub repository. Thank you.

---

## Links to fill in

- GitHub repository: <GitHub repository link>
- Demo video: <Demo video link>

## After recording

```
docker rm -f web01 app01 db01
```
