# Update BMC firmware of DPU

## Paremeters

* `bmc_url` -- URL of BMC firmware image

## Playbook examples

<details><summary markdown="span">manage-bf-bmc-fw.yaml</summary>
<pre><code>
---
- hosts: bmc
  user: "{{ remote_install_user }}"
  gather_facts: no # if using a bmc host, this will fail because ansible is not present
  become: true
  vars:
    bmc_url: "{{ foreman.foreman_mirror }}/{{ bmc.file }}"
  roles:
    - nvidia.dpu_ops.manage_bf_bmc_fw
</code></pre>
</details>
