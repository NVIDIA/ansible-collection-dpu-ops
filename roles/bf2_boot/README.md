# DPU (BF2) Boot
## Parameters

Ansible variable(s) to be defined:

* `pxe_boot_dev` - name of device to boot DPU from in `/etc/bf.cfg` of the installer. 
  Allowed values are:
   * `NET-OOB-IPV4`
   * `NET-NIC_P1-IPV4`
 
## Usage example

<details><summary markdown="span">bf2-boot-order.yml</summary>
<pre><code>
- hosts: bf2oob
  become: true
  user: "{{ remote_install_user }}"
  vars:
    pxe_boot_dev: "{{ bf2.pxe_boot_dev }}"
  roles:
    - nvidia.dpu_ops.bf2_boot
</code></pre>
</details>
