#!/usr/bin/python

###############################################################################
#
# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
###############################################################################

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import re
import sys


DOCUMENTATION = r'''
---
module: bf2_facts

short_description: Module for generating bf2 facts

version_added: "1.1.0"

description: MModule for generating bf2 facts

'''


EXAMPLES = r'''
- name: gather bf2 facts
  bf2_facts:
'''


RETURN = r'''
ansible_facts:
  description: Facts to add to ansible_facts.
  returned: always
  type: dict
  contains:
'''


UNDEFINED = 'UNDEFINED'


import shlex
import subprocess
from ansible.module_utils.basic import AnsibleModule

# singleton, cache of mlxconfig, key is pci/mst dev, val is dict()
nvconfig_cache = dict()
lspci_cache = dict()


class CommandError(Exception):
    """
    helper class for handling stderr failures
    """
    def __init__(self, stderr):
        self.stderr = stderr
    def __str__(self):
        return self.stderr


def execute(cmd):
    """
    Executes a command, will raise an error if stderr is not clean
    """
    if type(cmd) == str:
        cmd = shlex.split(cmd)
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(input=None, timeout=15)
        if proc.returncode != 0:
        # if stderr:
            raise CommandError(stderr)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
    return stdout.decode('utf-8')


def get_lines(cmd):
    return execute(cmd).rstrip().split('\n')


def get_first_result(results, key):
    for r in results:
        if key in r:
            return r
    return None
    # return next(filter(lambda r: key in r, results))


def has_query_privhost():
    lines = get_lines('mlxprivhost -h')
    return get_first_result(lines, 'query') is not None


def get_rshim_output(rshim_path):
    # File IO in the Popen call is unhappy w/ the special rshim files, so this call command is used
    subprocess.call("echo 'DISPLAY_LEVEL 1' > {}/misc".format(rshim_path), shell=True)
    lines = get_lines("cat {}/misc".format(rshim_path))
    # add in the rshim slot for later use
    lines.append("RSHIM_SLOT       {}".format(rshim_path))
    dev_name_line = get_first_result(lines, 'DEV_NAME')
    full_dev_name = shlex.split(dev_name_line)[1]
    return full_dev_name, lines


def get_mst_and_pci():
    # get all the lines with BlueField2 since those are the cards
    # Note that the -v flag will have 2 devices per card
    # the second device will be in the form of device.1
    # We discard the device.1's to not have duplicate devices
    lines = get_lines('mst status -v')
    # FIXME BlueField (1), BlueField3 ?
    bf_lines = [l for l in lines if 'BlueField' in l]
    # grab only the pcie device name
    mst_and_pci = [tuple(l.split()[1:3]) for l in bf_lines]
    # discard the devices with a period in the name
    return [l for l in mst_and_pci if '.' not in l[0]]


def _parse_mlxconfig(lines):
    """
    Input: lines of `mlxconfig -d .. q` output
    Output: dict
    """
#    in_hdr = True
    ret = dict()
    for l in lines:
#        if in_hdr:
#            if l.startswith('Configurations'):
#                in_hdr = False
#            continue
#        if not l:
#            continue
        ary = re.split(r'\s+', l)
        # print(repr(ary), file=sys.stderr)
        # (x, hdr, val) = re.split(r'\s+', l)
        if len(ary) >= 3 and ary[0] == '':
            ret[ary[1]] = ary[2]
    return ret


def get_mlxconfig(mst):
    global nvconfig_cache
    if mst in nvconfig_cache:
        return nvconfig_cache[mst]
    lines = get_lines("mlxconfig -d {} q".format(mst))
    ret = _parse_mlxconfig(lines)
    # needed for PRIS and ROY adapters:
    if 'PCI_DOWNSTREAM_PORT_OWNER' in ret:
        k = 'PCI_DOWNSTREAM_PORT_OWNER[4]'
        lines = get_lines("mlxconfig -d {} q {}".format(mst, k))
        r2 = _parse_mlxconfig(lines)
        ret[k] = r2[k]
    nvconfig_cache[mst] = ret
    return(ret)


def get_mode(mst):
    nvcfg = get_mlxconfig(mst)
    # print(f"(get_mode: {nvcfg['INTERNAL_CPU_MODEL']})", file=sys.stderr)
    # TODO what about NIC_MODE vs SNIC_MODE vs SEPARATED_MODE ?
    v = nvcfg.get('INTERNAL_CPU_MODEL', None)
    if v is not None:
        return 'embedded' if v == 'EMBEDDED_CPU(1)' else 'separated'
    else:
        return UNDEFINED


def get_vpd(pci):
    if pci in lspci_cache:
        return lspci_cache[pci]
    lines = get_lines("lspci -vvs {}".format(pci))
    rx = re.compile('^\s+\[(\w\w)\]\s[^:]+:\s(.*?)\s*$')
    ret = dict()
    for l in lines:
        m = rx.search(l)
        if m is None:
            continue
        ret[m.group(1)] = m.group(2)
    lspci_cache[pci] = ret
    return ret


def get_serial_number(pci):
    # lines = get_lines("lspci -vvs {}".format(pci))
    # line = get_first_result(lines, 'Serial number')
    # if line is None:
    #    return UNDEFINED
    # return line.split(":")[-1].strip()
    vpd = get_vpd(pci)
    return vpd.get('SN', UNDEFINED)



def get_part_number(pci):
    vpd = get_vpd(pci)
    return vpd.get('PN', UNDEFINED)
    # lines = get_lines("lspci -vvs {}".format(pci))
    # line = get_first_result(lines, 'Part number')
    # if line is None:
    #     return UNDEFINED
    # return line.split(":")[-1].strip()


def get_rshims_from_fs():
    # the case of no rshims should return an empty list, not a list of 1 empty item
    rshims = get_lines('find /dev -maxdepth 1 -name "rshim*"')
    if len(rshims) == 1 and not rshims[0]:
        return []
    return rshims


def get_rshim_from_pci(rshim_outs, pci):
    if not rshim_outs:
        return None
    # Split on the dot of the pci as the key in the rshim_outs
    # has a different dot version (62:00.0 vs 62:00.2)
    rshim_key = pci.split('.')[0]
    # There may not be rshim's on the host for a given card, so not finding
    # a result just means it is not found
    key = get_first_result(rshim_outs.keys(), rshim_key)
    if key is None:
        return []
    return rshim_outs.get(key)


def get_mac_from_rshim_output(rshim_out):
    line = get_first_result(rshim_out, 'PEER_MAC')
    return shlex.split(line)[1]


def get_rshim_slot_from_rshim_output(rshim_out):
    line = get_first_result(rshim_out, 'RSHIM_SLOT')
    return shlex.split(line)[1]


def get_restriction_level(mst):
    lines = get_lines("mlxprivhost -d {} q".format(mst))
    line = get_first_result(lines, 'level')
    return line.split(":")[1].strip().lower()


def get_versions(mst):
    lines = get_lines("mlxfwmanager -d {}".format(mst))
    versions = {}
    for line in lines:
        for phrase in ['FW', 'PXE', 'UEFI', 'UNKNOWN_ROM']:
            if phrase in line:
                # Some of the UEFI Virtio have 3 words before the version so this
                # takes that into consideration
                split = shlex.split(line)
                if (split[1] == 'Virtio'):
                    key = "{} {} {}".format(split[0], split[1], split[2])
                    versions[key] = split[3]
                else:
                    versions[split[0]] = split[1]
    return versions


def run_module():
    ansible_facts = {'bf2_devices': []}
    warnings = []

    module = AnsibleModule(
        argument_spec={},
        supports_check_mode=True
    )
    try:
        try:
            execute('mst start')
        except FileNotFoundError:
            # if mst is not installed on the machine, popen will throw this exception,
            # so it can be handled gracefully
            module.exit_json(ansible_facts=ansible_facts,
                             warnings="could not find the mst command, ensure that mlnx-ofed-all is installed")

        # validate if mlxprivhost can be used for query mode. some versions do not have the query flag
        can_query_privhost = has_query_privhost()

        rshims = get_rshims_from_fs()
        # rshim output will contain a key to the pcie device name with info inside it
        rshim_outs = {}

        # get all the rshim's on a single machine
        for rshim_path in rshims:
            full_dev_name, lines = get_rshim_output(rshim_path)
            rshim_outs[full_dev_name] = lines

        for mst, pci in get_mst_and_pci():
            rshim_out = get_rshim_from_pci(rshim_outs, pci)
            permission = get_restriction_level(mst) if can_query_privhost else UNDEFINED
            if permission == 'privileged':
                # many items only work in privileged mode
                ownership = get_mode(mst)
                versions = get_versions(mst)
            else:
                ownership = UNDEFINED
                versions = UNDEFINED


            ansible_facts['bf2_devices'].append({
                'mst': mst,
                'pci': pci,
                'ownership': ownership,
                'permission': permission,
                'serial_number': get_serial_number(pci),
                'part_number': get_part_number(pci),
                # Sort this out once the mac is not all 00's
                # 'mac': get_mac_from_rshim_output(rshim_out) if rshim_out else UNDEFINED,
                'rshim': get_rshim_slot_from_rshim_output(rshim_out) if rshim_out else UNDEFINED,
                'versions': versions,
                'nvconfig': nvconfig_cache.get(mst, {})
            })

        module.exit_json(ansible_facts=ansible_facts, warnings="")
    except Exception as e:
        module.fail_json(msg='An unhandled error occured', exception=e)


def main():
    run_module()


if __name__ == '__main__':
    main()
