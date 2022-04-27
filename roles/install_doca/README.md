# Install DOCA

The `install_doca` role is used to install [Nvidia DOCA SDK](https://developer.nvidia.com/networking/doca)
on x86 host.

## Parameters

* `doca.version` -- version of DOCA to install
* `doca.package` -- name of RPM/DEB package with DOCA SDK to install on x86 machine

The role couldn't parse HTML page to guess name of DEB/RPM package to install.

## Playbook examples

<details><summary markdown="span">manage-doca.yml</summary>
<pre><code>
---
- hosts: x86host
  user: "{{ remote_install_user }}"
  become: true
  vars:
    doca:
      version: 1.2.1
      package: doca-host-repo-ubuntu2004_1.2.1-0.1.5.1.2.006.5.5.2.1.7.0_amd64.deb
  roles:
    - nvidia.dpu_ops.install_doca
</code></pre>
</details>
