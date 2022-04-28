# Install CUDA on x86 or DPU

The `install_cuda` role is used to install Nvidia CUDA SDK
on x86 host or on DPU.

## Parameters

* `cuda_release` -- release of CUDA like `11.5.1`, `11.6.2`
* `cuda_arch` -- CPU architecture to install. Allowed values are:
  * `amd64`
  * `arm64`
* `mode` -- choose "DEB (network)" `deb_network` or "DEB (local)" `deb_local`


## Playbook examples

<details><summary markdown="span">setup_cuda_network.yml</summary>
<pre><code>
# Usage:
#   ansible-playbook setup_cuda_network.yml -v -e cuda_release=11.6.2 -e cuda_arch=arm64
---
- hosts: "{{ groups['foreman'][0] }}"
  user: "{{ remote_install_user }}"
  become: true
  roles:
    - nvidia.dpu_ops.prepare_cuda_repo

- hosts: bf2oob
  user: "{{ remote_install_user }}"
  become: true
  roles:
    - name: nvidia.dpu_ops.install_cuda
      mode: deb_network
      when: cuda_arch == "arm64"

- hosts: x86host
  user: "{{ remote_install_user }}"
  become: true
  roles:
    - name: nvidia.dpu_ops.install_cuda
      mode: deb_network
      when: cuda_arch == "amd64"
</code></pre>
</details>

<details><summary markdown="span">setup_cuda_local.yml</summary>
<pre><code>
# Usage:
#   ansible-playbook setup_cuda_local.yml -v -e cuda_release=11.6.2 -e cuda_arch=arm64
---
- hosts: "{{ groups['foreman'][0] }}"
  user: "{{ remote_install_user }}"
  become: true
  roles:
    - nvidia.dpu_ops.prepare_cuda_repo

- hosts: bf2oob
  user: "{{ remote_install_user }}"
  become: true
  roles:
    - name: nvidia.dpu_ops.install_cuda
      mode: deb_local
      when: cuda_arch == "arm64"

- hosts: x86host
  user: "{{ remote_install_user }}"
  become: true
  roles:
    - name: nvidia.dpu_ops.install_cuda
      mode: deb_local
      when: cuda_arch == "amd64"
</code></pre>
</details>
