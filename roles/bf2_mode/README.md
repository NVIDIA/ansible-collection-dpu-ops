# DPU (BF2) Mode

The `bf2_mode` role is used to:
1. set restricted mode and block the host from accessing the DPU or grant the access
2. change an "ownernership", actually switch DPU NIC mode between "separated host" and "smartnic"

For more information about the DPU modes of operation, see the 
[NVIDIA Mellanox BlueField DPU SW Modes of Operation](https://docs.nvidia.com/networking/display/BlueFieldSWv35111601/Modes+of+Operation#ModesofOperation-SeparatedHost) page. 

## Parameters

Ansible variable(s) to be defined:

* `new_bf_mode`  - is used set restricted mode and block the host from accessing the DPU
  Allowed values are:
  * `privileged`
  * `restricted`

* `new_bf_ownership` - the DPU may be placed in either separated or embedded ownership mode. 
  Allowed values are:
  * `SEPARATED_HOST`
  * `EMBEDDED_CPU`
 
## Playbook examples

<details><summary markdown="span">bf2_mode.yml</summary>
<pre><code>
---
- hosts: bf2oob
  user: "{{ remote_install_user }}"
  become: true
  pre_tasks:
    - name: Check for required variables
      fail:
        msg: "Invalid security mode, new_bf_mode should either be restricted or privileged"
      when: new_bf_mode not in bf2.security_modes
  vars:
    bmc_host: "{{ hostvars[non_bf2_host]['bmc_ip'] }}"
    bmc_user: "{{ hostvars[non_bf2_host]['bmc_user'] }}"
    bmc_password: "{{ hostvars[non_bf2_host]['bmc_password'] }}"
    run_on: "{{ groups['foreman'][0] }}"
  roles:
    - nvidia.dpu_ops.bf2_mode
  post_tasks:
    - name: wait for machine to be back online
      wait_for:
        host: "{{ non_bf2_host }}"
        port: 22
        timeout: 900
        delay: 60
      delegate_to: "{{ groups['foreman'][0] }}"
</code></pre>
</details>
