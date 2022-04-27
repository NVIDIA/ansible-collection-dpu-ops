# Set RSHIM ownership

The `manage_rshim_owner` role allows to set owner of DPU RSHIM interface.
It could be either BMC or x86 host.

## Parameters

* `bf_target` -- who is the owner of RSHIM: `bmc` or `x86`

## Playbook example

<details><summary markdown="span">bf2_mode.yml</summary>
<pre><code>
- hosts: "bmc"
  user: "{{ remote_install_user }}"
  become: true
  gather_facts: False
  vars:
    bf_target: "bmc"  # internal variable for the non_bf2_host regex
    ansible_fqdn: "{{ inventory_hostname }}" # this hack is because facts are not gathered and the non_bf2_host uses it
    x86_host: "{{ non_bf2_host }}"
    bmc_host: "{{ inventory_hostname }}"
  roles:
    - nvidia.dpu_ops.manage_rshim_owner
</code></pre>
</details>
