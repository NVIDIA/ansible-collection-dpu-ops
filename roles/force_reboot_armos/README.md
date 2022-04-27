# Force reboot of ARM OS of DPU
The `force_reboot_armos` role is used to reboot "ARM OS" of DPU 
from x86 host side

## Parameters

## Playbook examples

<details><summary markdown="span">force_reboot_armos.yaml</summary>
<pre><code>
---
- hosts: all
  user: "{{ remote_install_user }}"
  gather_facts: no
  become: true
  pre_tasks:
    - name: set is_bmc
      set_fact:
        is_bmc: "{{ inventory_hostname.startswith('bmc') }}"
  roles:
    - nvidia.dpu_ops.force_reboot_armos
</code></pre>
</details>

