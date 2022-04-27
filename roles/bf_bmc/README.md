# BF BMC
This role is used to manage power state of x86 or DPU using IPMI protocol

## Parameters

The `main.yaml` tasks requires following parameter to be specified:

* `bmc_action` -- IPMI command to execute on BMC

## Standalone tasks

* `chassis_power_off.yaml`
* `chassis_power_on.yaml`
* `powercycle.yml`

## Playbook example

<details><summary markdown="span">bf2_mode.yml</summary>
<pre><code>
---
- hosts: "bmc"
  user: "{{ remote_install_user }}"
  become: true
  gather_facts: False
  vars:
    bmc_action: "chassis power cycle"
    bmc_host: "{{ inventory_hostname }}"
    bmc_user: "{{ ansible_user }}"
    bmc_password: "{{ ansible_password }}"
    run_on: "{{ groups['foreman'][0] }}"
  roles:
    - nvidia.dpu_ops.bf_bmc
</code></pre>
</details>

<details><summary markdown="span">powercycle.yml</summary>
<pre><code>
---
- hosts: bf2oob
  user: "{{ remote_install_user }}"
  become: true
  gather_facts: true

  vars:
    bmc_host: "{{ hostvars[non_bf2_host]['bmc_ip'] }}"
    bmc_user: "{{ hostvars[non_bf2_host]['bmc_user'] }}"
    bmc_password: "{{ hostvars[non_bf2_host]['bmc_password'] }}"
    run_on: "{{ groups['foreman'][0] }}"
  tasks:
    - name: power-cycle x86 host
      include_role:
        name: nvidia.dpu_ops.bf_bmc
        tasks_from: powercycle.yml
</code></pre>
</details>
