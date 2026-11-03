# Base image for the lab "servers" (web01, app01, db01).
# Just Ubuntu + systemd + sshd + python3, everything else is done by Ansible.
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends systemd systemd-sysv openssh-server python3 sudo iproute2 ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ansible user with passwordless sudo, key based login only
RUN useradd -m -s /bin/bash ansible && \
    echo "ansible ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ansible && chmod 440 /etc/sudoers.d/ansible && \
    mkdir -p /home/ansible/.ssh && chmod 700 /home/ansible/.ssh
COPY ansible_key.pub /home/ansible/.ssh/authorized_keys
RUN chown -R ansible:ansible /home/ansible/.ssh && chmod 600 /home/ansible/.ssh/authorized_keys && \
    sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    systemctl enable ssh

STOPSIGNAL SIGRTMIN+3
CMD ["/sbin/init"]
