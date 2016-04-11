# Phase deployment Ansible playbooks

Here is a collection of [Ansible playbooks](https://www.ansible.com/) to help
with Phase hosting management and deployment.

## Quickstart

Use `./hosts.example` as a blueprint for an [Ansible inventory
file](http://docs.ansible.com/ansible/intro_inventory.html). You can edit the
`/etc/ansible/hosts` file (Ansible default) or create a local `hosts` file and
reference it with the `-i` option.

Make sure your ssh public key is uploaded on every server you try to run a task
on.

Deploy code to all active Phase instances in a few commands:

    ansible-playbook -i hosts configure.yml
    ansible-playbook -i hosts deploy.yml

To only deploy to staging installations:

    ansible-playbook -i hosts -l staging configure.yml
    ansible-playbook -i hosts -l staging deploy.yml

To deploy to a single host:

    ansible-playbook -i hosts -l phase.mycompany.com configure.yml
    ansible-playbook -i hosts -l phase.mycompany.com deploy.yml


## Playbooks

Here is a list of available playbooks.

 * `aptitude_update`: aptitude update && aptitude safe-upgrade.
 * `configure`: prepare and configure the phase vm.
 * `deploy`: deploy phase in the latest version.
 * `es_reindex`: Start document reindexing in ES.


## Inventory file

Servers are grouped to make playbooks easier to apply.

Aptitude update *everything*:

    ansible-playbook -i hosts aptitude_update.yml

Update only physical hosts, i.e bare metal servers hosting lxc virtual
machines:

    ansible-playbook -i hosts -l hosts aptitude_update.yml

Update only virtual machines, i.e actual phase installations in lxc containers:

    ansible-playbook -i hosts -l vms aptitude_update.yml

Update only staging environments:

    ansible-playbook -i hosts -l staging aptitude_update.yml

Update only production environments:

    ansible-playbook -i hosts -l prod aptitude_update.yml

## Local configuration

### Github authentication

Some of Phase dependencies are hosted as private git repositories (e.g
additional document apps) on Github.

We think asking for a Githb login / password every time the deployment playbook
runs would be tedious, and so would be generating ssh keys for every Phase
instance.

Hence we use [SSH Agent
Forwarding](https://developer.github.com/guides/using-ssh-agent-forwarding/),
so your local ssh authentication will be used by the remote server. There are a
few things you want to setup for this to work.

 * Generate an ssh key and upload your personal public key on Github.
 * Configure the ssh host to enable agent forwarding.

See the next section.

### SSH Config

Here is a sample `~/.ssh/config`:

    # My company physical host
    Host mycompany.com
        HostName my.server.dns
        User root

    # A Phase instance on a virtual machine with a public ip
    Host phase.mycompany.com
        HostName 1.2.3.4
        User root
        ForwardAgent yes

    # Another physical host
    Host myclient.com
        HostName my.client.dns
        User root
        ForwardAgent yes

    # A Phase instance on a LXC virtual machine and a local ip only
    Host phasetest.myclient.com
        User root
        ProxyCommand ssh myclient.com nc phasetest 22
        ForwardAgent yes
