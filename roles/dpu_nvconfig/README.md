# Set nvconfig parameters of DPU

The `dpu_nvconfig` role use use to:
* set link type (ETH or IB)
* set NIC mode
* set GPU owner 

## Parameters

1. Set link type (ETH or IB)
  * `link_type_p1`
  * `link_type_p2`

2. Set NIC mode:
  * `dpu_nic_mode` allowed values: `ConnectX` or `SmartNIC`

3. Set GPU owner for ROY adapter (DPU+GPU)
  * `gpu_owner` allowed values: `ARM` or `X86`

## Playbook examples

<details><summary markdown="span">set_vpi_mode.yaml</summary>
<pre><code>
---
- hosts: bf2oob
  user: "{{ remote_install_user }}"
  become: true
  gather_facts: true
  pre_tasks:
    - name: Check for required variables
      fail:
        msg: "Neither link_type_p1 nor link_type_p2 variables defined. Allowed values: ETH or IB"
      when:
        - not link_type_p1 is defined
        - not link_type_p2 is defined

  vars:
    bmc_host: "{{ hostvars[non_bf2_host]['bmc_ip'] }}"
    bmc_user: "{{ hostvars[non_bf2_host]['bmc_user'] }}"
    bmc_password: "{{ hostvars[non_bf2_host]['bmc_password'] }}"
    run_on: "{{ groups['foreman'][0] }}"
    link_type_p1: ETH
    link_type_p2: IB

  roles:
    - nvidia.dpu_ops.dpu_nvconfig

  post_tasks:
    - name: reboot x86 host block
      block:
        - name: notify about reboot
          debug:
            msg: "!!! Reboot of {{ non_bf2_host }} is scheduled (playbook handler)!!!"
        - name: power-cycle x86 host
          include_role:
            name: nvidia.dpu_ops.bf_bmc
            tasks_from: powercycle.yml
      when: should_reboot is defined
</code></pre>
</details>

<details><summary markdown="span">set_nic_mode-cx.yaml</summary>
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

  roles:
    - {name: nvidia.dpu_ops.dpu_nvconfig,
       dpu_nic_mode: ConnectX}

  post_tasks:
    - name: power-cycle x86 host
      include_role:
        name: nvidia.dpu_ops.bf_bmc
        tasks_from: powercycle.yml
    when: should_reboot is defined
</code></pre>
</details>

<details><summary markdown="span">set_nic_mode-snic.yaml</summary>
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

  roles:
    - {name: nvidia.dpu_ops.dpu_nvconfig,
       dpu_nic_mode: SmartNIC}

  post_tasks:
    - name: power-cycle x86 host
      include_role:
        name: nvidia.dpu_ops.bf_bmc
        tasks_from: powercycle.yml
    when: should_reboot is defined
</code></pre>
</details>

<details><summary markdown="span">set_gpu_mode.yaml</summary>
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

  roles:
    - {name: nvidia.dpu_ops.dpu_nvconfig,
       gpu_owner: ARM}

  post_tasks:
    - name: power-cycle x86 host
      include_role:
        name: nvidia.dpu_ops.bf_bmc
        tasks_from: powercycle.yml
    when: should_reboot is defined
</code></pre>
</details>
