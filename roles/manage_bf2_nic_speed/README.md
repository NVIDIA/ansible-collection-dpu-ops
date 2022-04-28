# Set ethernet link speed of DPU ports

## Parameters

* `p0_nic_speed_options` -- speed for port #1
* `p1_nic_speed_options` -- speed for port #2

## Playbook examples

<details><summary markdown="span">manage-bf2-nic-speed.yaml</summary>
<pre><code>
---
- hosts: bf2oob
  user: "{{ remote_install_user }}"
  become: true
  vars:
    p0_nic_speed_options: "{{ bf2.p0_nic_speed_options }}"
    p1_nic_speed_options: "{{ bf2.p1_nic_speed_options }}"
  roles:
    - nvidia.dpu_ops.manage_bf2_nic_speed
</code></pre>
</details>


