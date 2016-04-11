# Phase deployment Ansible playbooks

Here is a set of [Ansible playbooks](https://www.ansible.com/) to provision,
install and update Phase installations.


## Quickstart

Use `./hosts.example` as a blueprint for an [Ansible inventory
file](http://docs.ansible.com/ansible/intro_inventory.html). You can edit the
`/etc/ansible/hosts` file (Ansible default) or create a local `hosts` file and
reference it with the `-i` option.

Make sure your ssh public key is uploaded on every server you try to run a task
on.

Configure the servers and install Phase on every instance:

    ansible-playbook -i hosts site.yml

Only deploy to staging installations:

    ansible-playbook -i hosts -l staging site.yml

To deploy to a single host:

    ansible-playbook -i hosts -l www.phase-demo.mycompany.com site.yml


## Playbooks

We tried to structure playbooks according to [Ansible's best
practices](http://docs.ansible.com/ansible/playbooks_best_practices.html),
splitting top-level playbooks into roles.

The top level playbook is `site.yml`. Running this playbook will entirely
configure the server and install Phase on it. Check the file content to see
what top-level playbooks are available.


## Staging and production

It's easy to only deploy in certain environments, e.g in staging or production.
All you need to do is create groups in your inventory file and target them
using `ansible-playbook`'s `-l` option.

    # /etc/ansible/hosts
    [appservers]
    phase.mycompany.com
    phase-staging.mycompany.com

    [staging]
    phase-staging.mycompany.com

To only deploy to staging environments:

    ansible-playbook -l staging site.yml


## Delivering different Phase versions to different environments

What if you run two Phase instance with different versions? Simply define
different groups in your inventory, create a
`/etc/ansible/group_vars/<group>.yml`, and give the `project_version` variable
the git commit name you want to fetch (can be a branch or a tag).

You can also install additional applications using the `document_apps`
variable.

In `/etc/ansible/hosts`:

    [appservers]
    phase.mycompany.com
    phase.myclient.com

    [myclient]
    phase.myclient.com

In `/etc/ansible/group_vars/myclient.yml`:

    project_version: master
    document_apps:
      - { repo: "git@github.com:mycompany/myclientapps.git", name: "myclientapps" }


`project_version`'s default value is `master`.

**Warning**: If you configure a custom commit id in `project_version`, you
*must* make sure the same id exists in *all* additional document apps listed in
`document_apps`.


## Different Phase versions to different hosts

What if you want to deliver different Phase versions to different environments
for the same client? Here is an example.

In `/etc/ansible/hosts`:

    [appservers]
    phase.mycompany.com
    myclient-phase.mycompany.com
    myclient-phase-staging.mycompany.com

    [staging]
    phase-staging.mycompany.com

    [myclient]
    myclient-phase.mycompany.com
    myclient-phase-staging.mycompany.com

In `/etc/ansible/group_vars/myclient.yml`:

    document_apps:
      - { repo: "git@github.com:mycompany/myclientapps.git", name: "myclientapps" }

In `/etc/ansible/host_vars/myclient-phase.mycompany.com.yml`:

    project_version: v1.0.1

In `/etc/ansible/host_vars/myclient-phase-staging.mycompany.com.yml`:

    project_version: v1.0.2


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
