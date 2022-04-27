# Update DPU NIC firmware

The `manage_bf2_fw` roles updates NIC firmware of DPU and power-cycle the x86 host

## Playbook examples

<details><summary markdown="span">manage-bf2-fw.yaml</summary>
<pre><code>
---
- hosts: bf2oob
  user: "{{ remote_install_user }}"
  become: true
  vars:
    bmc_host: "{{ hostvars[non_bf2_host]['bmc_ip'] }}"
    bmc_user: "{{ hostvars[non_bf2_host]['bmc_user'] }}"
    bmc_password: "{{ hostvars[non_bf2_host]['bmc_password'] }}"
    run_on: "{{ groups['foreman'][0] }}"
  roles:
    - nvidia.dpu_ops.manage_bf2_fw
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
