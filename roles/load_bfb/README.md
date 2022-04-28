# Load BFB image into DPU over RSHIM 

## Parameters

* `local_bfb` -- location of BFB image on local FS
* `bfb_url` -- URL of BFB image to be downloaded on x86 host
* `boot_mac`  -- MAC-address of network interface to boot from

## Playbook examples

<details><summary markdown="span">load-bfb.yaml</summary>
<pre><code>
---
- hosts: bf2:bf2oob:bmc
  user: "{{ remote_install_user }}"
  gather_facts: no # if using a bmc host, this will fail because ansible is not present
  become: true
  vars:
    bfb_url: "{{ foreman.foreman_mirror }}/{{ product_version }}/{{ bfb.file }}"
    cloudinit_hostname: "{{ inventory_hostname | regex_replace('bmc-','') }}"
    cloudinit_ntp_host: "{{ subnet_dns_primary }}"
    cloudinit_dns_host: "{{ subnet_dns_primary }}"
    tmfifo_ip: "{{ hostvars[inventory_hostname].tmfifo_ip | default('192.168.100.2') }}/28"
    tmfifo_mac: "{{ hostvars[inventory_hostname].tmfifo_mac | default('00:1a:ca:ff:ff:01') }}"
    cloudinit_mtu: "{{ network_mtu }}"
    ovs_mtu: "{{ network_mtu|int + 50 }}"
    cloudinit_domain: "{{ domain }}"
    bfcfg_template: "roles/load_bfb/templates/bf2_ndo.cfg.j2"
    ansible_fqdn: "{{ inventory_hostname }}" # this hack is because facts are not gathered and the non_bf2_host uses it
  pre_tasks:
    - name: set is_bmc
      set_fact:
        is_bmc: "{{ inventory_hostname.startswith('bmc') }}"
    - name: bmc operations
      block:
        - name: set hosts
          set_fact:
            x86_host: "{{ foreman_url }}"
            dpu_host: "{{ inventory_hostname | regex_replace('bmc-','') }}"
        - name: set bmc facts
          set_fact:
            boot_mac: "{{ hostvars[dpu_host]['oob_mac'] if bf2.oob_provision else hostvars[dpu_host]['primary_mac'] }}"
            local_bfb: "/var/www/{{ product_version }}/{{ bfb.file }}" # directly manipulate the foreman filesystem
      when: inventory_hostname.startswith('bmc')
    - name: x86 host operations
      block:
        - name: set hosts
          set_fact:
            x86_host: "{{ non_bf2_host }}"
            dpu_host: "{{ inventory_hostname | regex_replace('oob-','') }}"
        - name: set non bmc facts
          set_fact:
            boot_mac: "{{ hostvars[dpu_host]['oob_mac'] if bf2.oob_provision else hostvars[dpu_host]['primary_mac'] }}"
            local_bfb: "{{ bf2.download_local_path }}/{{ bfb.file }}"
        - name: Create bfb temp dir
          file:
            state: directory
            path: "{{ bf2.download_local_path }}"
            owner: root
            group: root
            mode: "0644"
          delegate_to: "{{ x86_host }}"
        - name: Download bfb from web server
          get_url:
            url: "{{ bfb_url }}"
            dest: "{{ bf2.download_local_path }}"
            validate_certs: "{{ foreman.validate_certs }}"
          delegate_to: "{{ x86_host }}"
      when: not inventory_hostname.startswith('bmc')
  roles:
    - nvidia.dpu_ops.load_bfb
</code></pre>
</details>
