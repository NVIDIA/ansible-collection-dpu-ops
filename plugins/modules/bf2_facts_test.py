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

import bf2_facts
import shlex
import unittest
from unittest.mock import patch


def generate_rshim_output(mock_execute, pci, rshim, mac='00:00:00:00:00:00'):
    example = """DISPLAY_LEVEL   1 (0:basic, 1:advanced, 2:log)
BOOT_MODE       1 (0:rshim, 1:emmc, 2:emmc-boot-swap)
BOOT_TIMEOUT    100 (seconds)
DROP_MODE       0 (0:normal, 1:drop)
SW_RESET        0 (1: reset)
DEV_NAME        pcie-0000:{}.2
DEV_INFO        BlueField-2(Rev 1)
BOOT_RESET_SKIP 0 (1: skip)
PEER_MAC        {} (rw)
PXE_ID          0x00000000 (rw)
VLAN_ID         0 0 (rw)
""".format(pci, mac)
    mock_execute.return_value = example
    return bf2_facts.get_rshim_output(rshim)


class Test(unittest.TestCase):
    @patch('bf2_facts.execute')
    def test_has_query_privhost_new_version(self, mock_execute):
        example = """usage: mlxprivhost [-h] [-v] --device DEVICE [--disable_rshim] [--disable_tracer] [--disable_counter_rd] [--disable_port_owner] {r,restrict,p,privilege,q,query}

restrict or privilege host
Note: New configurations takes effect immediately.
Note: privileged host - host has all supported privileges.
      restricted host - host is not allowed to modify global
      per port/parameters or access other hosts parametersis.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

Options:
  --device DEVICE, -d DEVICE
                        Device to work with.
  --disable_rshim       When TRUE, the host does not have an RSHIM function
                        to access the embedded CPU registers
  --disable_tracer      When TRUE, the host will not be allowed to own the Tracer
  --disable_counter_rd  When TRUE, the host will not be allowed to read Physical port counters
  --disable_port_owner  When TRUE, the host will not be allowed to be Port Owner

Commands:
  {r,restrict,p,privilege,q,query}
                        restrict:  Set host 1 (ARM) privileged, host 0 (x86_64) restricted.
                        privilege: Set host 1 (ARM) privileged, host 0 (x86_64) privileged
                                   (back to default).
                        query:     Query current host configuration.
"""
        mock_execute.return_value = example
        self.assertTrue(bf2_facts.has_query_privhost())

    @patch('bf2_facts.execute')
    def test_has_query_privhost_old_version(self, mock_execute):
        example = """usage: mlxprivhost [-h] [-v] --device DEVICE [--disable_rshim] [--disable_tracer] [--disable_counter_rd] [--disable_port_owner] {r,restrict,p,privilege}

restrict or privilege host
Note: New configurations takes effect immediately.
Note: privileged host - host has all supported privileges.
      restricted host - host is not allowed to modify global
      per port/parameters or access other hosts parametersis.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

Options:
  --device DEVICE, -d DEVICE
                        Device to work with.
  --disable_rshim       When TRUE, the host does not have an RSHIM function
                        to access the embedded CPU registers
  --disable_tracer      When TRUE, the host will not be allowed to own the Tracer
  --disable_counter_rd  When TRUE, the host will not be allowed to read Physical port counters
  --disable_port_owner  When TRUE, the host will not be allowed to be Port Owner

Commands:
  {r,restrict,p,privilege}
                        restrict:  Set host 1 (ARM) privileged, host 0 (x86_64) restricted.
                        privilege: Set host 1 (ARM) privileged, host 0 (x86_64) privileged
                                   (back to default).
"""
        mock_execute.return_value = example
        self.assertFalse(bf2_facts.has_query_privhost())

    @patch('bf2_facts.execute')
    @patch('subprocess.call')
    def test_get_rshim_output(self, call, mock_execute):
        example = """DISPLAY_LEVEL   1 (0:basic, 1:advanced, 2:log)
BOOT_MODE       1 (0:rshim, 1:emmc, 2:emmc-boot-swap)
BOOT_TIMEOUT    100 (seconds)
DROP_MODE       0 (0:normal, 1:drop)
SW_RESET        0 (1: reset)
DEV_NAME        pcie-0000:e2:00.2
DEV_INFO        BlueField-2(Rev 1)
BOOT_RESET_SKIP 0 (1: skip)
PEER_MAC        00:00:00:00:00:00 (rw)
PXE_ID          0x00000000 (rw)
VLAN_ID         0 0 (rw)
"""
        mock_execute.return_value = example
        actual_rshim_slot = '/dev/rshim100'
        key, val = generate_rshim_output(mock_execute, 'e2:00', actual_rshim_slot)
        self.assertEqual(key, 'pcie-0000:e2:00.2')
        self.assertEqual(len(val), 12)
        rshim_slot = shlex.split([l for l in val if 'RSHIM_SLOT' in l][0])[1]
        self.assertEqual(rshim_slot, actual_rshim_slot)

    @patch('bf2_facts.execute')
    def test_get_mst_and_pci(self, mock_execute):
        example = """MST modules:
------------
    MST PCI module is not loaded
    MST PCI configuration module loaded
PCI devices:
------------
DEVICE_TYPE             MST                           PCI       RDMA            NET                       NUMA
BlueField2(rev:1)       /dev/mst/mt41686_pciconf0.1   e2:00.1   mlx5_1          net-ens7f1                1

BlueField2(rev:1)       /dev/mst/mt41686_pciconf0     e2:00.0   mlx5_0          net-ens7f0                1

"""
        mock_execute.return_value = example
        mst_and_pci = bf2_facts.get_mst_and_pci()
        self.assertEqual(len(mst_and_pci), 1)
        self.assertEqual(mst_and_pci[0][0], '/dev/mst/mt41686_pciconf0')
        self.assertEqual(mst_and_pci[0][1], 'e2:00.0')

    @patch('bf2_facts.execute')
    def test_get_mode(self, mock_execute):
        example = """
Device #1:
----------

Device type:    BlueField2
Name:           MBF2M516A-EEEO_Ax
Description:    BlueField-2 E-Series SmartNIC 100GbE/EDR VPI Dual-Port QSFP56; PCIe Gen4 x16; Crypto Enabled; 16GB on-board DDR; 1GbE OOB management; FHHL
Device:         /dev/mst/mt41686_pciconf0

Configurations:                              Next Boot
         MEMIC_BAR_SIZE                      0
         MEMIC_SIZE_LIMIT                    _256KB(1)
         HOST_CHAINING_MODE                  DISABLED(0)
         HOST_CHAINING_CACHE_DISABLE         False(0)
         HOST_CHAINING_DESCRIPTORS           Array[0..7]
         HOST_CHAINING_TOTAL_BUFFER_SIZE     Array[0..7]
         INTERNAL_CPU_MODEL                  EMBEDDED_CPU(1)
         _INTERNAL_CPU_MODEL                  SEPARATED_HOST(0)
         FLEX_PARSER_PROFILE_ENABLE          0
         PROG_PARSE_GRAPH                    False(0)
         FLEX_IPV4_OVER_VXLAN_PORT           0
         ROCE_NEXT_PROTOCOL                  254
         ESWITCH_HAIRPIN_DESCRIPTORS         Array[0..7]
         ESWITCH_HAIRPIN_TOT_BUFFER_SIZE     Array[0..7]
         PF_BAR2_SIZE                        0
         NON_PREFETCHABLE_PF_BAR             False(0)
         VF_VPD_ENABLE                       False(0)
         PER_PF_NUM_SF                       False(0)
         LINK_TYPE_P1                        ETH(2)
         LINK_TYPE_P2                        ETH(2)
"""
        mock_execute.return_value = example
        mode = bf2_facts.get_mode('/dev/mst/mt41686_pciconf0')
        self.assertEqual(mode, 'embedded')

        example = """
Device #1:
----------

Device type:    BlueField2
Name:           MBF2M516A-EEEO_Ax
Description:    BlueField-2 E-Series SmartNIC 100GbE/EDR VPI Dual-Port QSFP56; PCIe Gen4 x16; Crypto Enabled; 16GB on-board DDR; 1GbE OOB management; FHHL
Device:         /dev/mst/mt41686_pciconf0.1

Configurations:                              Next Boot
         MEMIC_BAR_SIZE                      0
         INTERNAL_CPU_MODEL                  SEPARATED_HOST(0)
"""
        mock_execute.return_value = example
        mode = bf2_facts.get_mode('/dev/mst/mt41686_pciconf0.1')
        self.assertEqual(mode, 'separated')

    @patch('bf2_facts.execute')
    def test_get_part_and_serial_number(self, mock_execute):
        example = """e2:00.0 Ethernet controller: Mellanox Technologies MT42822 BlueField-2 integrated ConnectX-6 Dx network controller (rev 01)
        Subsystem: Mellanox Technologies MT42822 BlueField-2 integrated ConnectX-6 Dx network controller
        Physical Slot: 7-1
        Control: I/O- Mem+ BusMaster+ SpecCycle- MemWINV- VGASnoop- ParErr+ Stepping- SERR+ FastB2B- DisINTx+
        Status: Cap+ 66MHz- UDF- FastB2B- ParErr- DEVSEL=fast >TAbort- <TAbort- <MAbort- >SERR- <PERR- INTx-
        Latency: 0
        Interrupt: pin A routed to IRQ 229
        NUMA node: 1
        Region 0: Memory at 47ea2000000 (64-bit, prefetchable) [size=32M]
        Region 2: Memory at 47ea1000000 (64-bit, prefetchable) [size=8M]
        Expansion ROM at <ignored> [disabled]
        Capabilities: [48] Vital Product Data
                Product Name: BlueField-2 DPU 100GbE/EDR/HDR100 VPI Dual-Port QSFP56, Crypto Enabled, 16GB on-board DDR, 1GbE OOB management, Tall Bracket

                Read-only fields:
                        [PN] Part number: MBF2M516A-EEEOT
                        [EC] Engineering changes: A4
                        [V2] Vendor specific: MBF2M516A-EEEOT
                        [SN] Serial number: MT2050X00614
                        [V3] Vendor specific: 9c20a1608d3feb118000043f72ff4c16
                        [VA] Vendor specific: MLX:MN=MLNX:CSKU=V2:UUID=V3:PCI=V0:MODL=BF2M516A
                        [V0] Vendor specific: PCIeGen4 x16
                        [RV] Reserved: checksum good, 1 byte(s) reserved
                End
"""
        mock_execute.return_value = example
        bf2_facts.lspci_cache = dict()  # need to clean it up
        serial_number = bf2_facts.get_serial_number('e2:00.0')
        self.assertEqual('MT2050X00614', serial_number)
        part_number = bf2_facts.get_part_number('e2:00.0')
        self.assertEqual('MBF2M516A-EEEOT', part_number)


    @patch('bf2_facts.execute')
    def test_no_vpd(self, mock_execute):
        example = """e2:00.0 Ethernet controller: Mellanox Technologies MT42822 BlueField-2 integrated ConnectX-6 Dx network controller (rev 01)
        Subsystem: Mellanox Technologies MT42822 BlueField-2 integrated ConnectX-6 Dx network controller
        Physical Slot: 7-1
        Control: I/O- Mem+ BusMaster+ SpecCycle- MemWINV- VGASnoop- ParErr+ Stepping- SERR+ FastB2B- DisINTx+
        Status: Cap+ 66MHz- UDF- FastB2B- ParErr- DEVSEL=fast >TAbort- <TAbort- <MAbort- >SERR- <PERR- INTx-
        Latency: 0
        Interrupt: pin A routed to IRQ 229
        NUMA node: 1
        Region 0: Memory at 47ea2000000 (64-bit, prefetchable) [size=32M]
        Region 2: Memory at 47ea1000000 (64-bit, prefetchable) [size=8M]
        Expansion ROM at <ignored> [disabled]
        Capabilities: [48] Vital Product Data
                End
"""
        mock_execute.return_value = example
        bf2_facts.lspci_cache = dict()  # need to clean it up
        serial_number = bf2_facts.get_serial_number('e2:00.0')
        self.assertEqual('UNDEFINED', serial_number)
        part_number = bf2_facts.get_part_number('e2:00.0')
        self.assertEqual('UNDEFINED', part_number)
    @patch('bf2_facts.execute')
    def test_get_rshims_from_fs(self, mock_execute):
        example = """/dev/rshim0
/dev/rshim1
/dev/rshim100
"""
        mock_execute.return_value = example
        rshims = bf2_facts.get_rshims_from_fs()
        self.assertEqual(3, len(rshims))

    @patch('bf2_facts.execute')
    @patch('subprocess.call')
    def test_get_rshim_from_pci(self, call, mock_execute):
        rshim_outs = {}
        pci_1 = 'aa:00'
        pci_2 = 'bb:00'
        for k,v in [(pci_1, '/dev/rshim1'), (pci_2, '/dev/rshim2')]:
            name, lines = generate_rshim_output(mock_execute, k, v)
            rshim_outs[name] = lines
        rshim_out = bf2_facts.get_rshim_from_pci(rshim_outs, pci_1)
        pci = [l for l in rshim_out if 'DEV_NAME' in l][0]
        self.assertTrue(pci_1 in pci)
        # empty case
        self.assertIsNone(bf2_facts.get_rshim_from_pci([], pci_1))

    @patch('bf2_facts.execute')
    @patch('subprocess.call')
    def test_get_mac_from_rshim_output(self, call, mock_execute):
        # first get some rshim_out data populated
        rshim_outs = {}
        pci = 'aa:00'
        mac = '01:01:01:01:01:01'
        name, lines = generate_rshim_output(mock_execute, pci, '/dev/rshim0', mac=mac)
        rshim_outs[name] = lines
        rshim_out = bf2_facts.get_rshim_from_pci(rshim_outs, pci)

        out_mac = bf2_facts.get_mac_from_rshim_output(rshim_out)
        self.assertEqual(mac, out_mac)

    @patch('bf2_facts.execute')
    @patch('subprocess.call')
    def test_get_rshim_slot_from_rshim_output(self, call, mock_execute):
        # first get some rshim_out data populated
        rshim_outs = {}
        pci = 'aa:00'
        rshim_slot = '/dev/rshim100'
        name, lines = generate_rshim_output(mock_execute, pci, rshim_slot)
        rshim_outs[name] = lines
        rshim_out = bf2_facts.get_rshim_from_pci(rshim_outs, pci)

        out_rshim_slot = bf2_facts.get_rshim_slot_from_rshim_output(rshim_out)
        self.assertEqual(rshim_slot, out_rshim_slot)

    @patch('bf2_facts.execute')
    def test_get_restriction_level(self, mock_execute):
        example = """Current device configurations:
------------------------------
level                         : PRIVILEGED

Port functions status:
-----------------------
disable_rshim                 : FALSE
disable_tracer                : FALSE
disable_port_owner            : FALSE
disable_counter_rd            : FALSE

"""
        mock_execute.return_value = example
        level = bf2_facts.get_restriction_level('/dev/mst/mt41686_pciconf0')
        self.assertEqual(level, 'privileged')

    @patch('bf2_facts.execute')
    def test_get_versions(self, mock_execute):
        example = """Querying Mellanox devices firmware ...

Device #1:
----------

  Device Type:      BlueField2
  Part Number:      MBF2M516A-EEEO_Ax
  Description:      BlueField-2 E-Series SmartNIC 100GbE/EDR VPI Dual-Port QSFP56; PCIe Gen4 x16; Crypto Enabled; 16GB on-board DDR; 1GbE OOB management; FHHL
  PSID:             MT_0000000559
  PCI Device Name:  /dev/mst/mt41686_pciconf0
  Base MAC:         043f72a45a9c
  Versions:         Current        Available
     FW             24.29.2008     N/A
     PXE            3.6.0205       N/A
     UEFI           14.22.0019     N/A
     UNKNOWN_ROM    22.1.0011      N/A
     UEFI Virtio x  1.2.3.4

  Status:           No matching image found

"""
        mock_execute.return_value = example
        versions = bf2_facts.get_versions('/dev/mst/mt41686_pciconf0')
        self.assertEqual(versions['FW'], '24.29.2008')
        self.assertEqual(versions['PXE'], '3.6.0205')
        self.assertEqual(versions['UEFI'], '14.22.0019')
        self.assertEqual(versions['UNKNOWN_ROM'], '22.1.0011')
        self.assertEqual(versions['UEFI Virtio x'], '1.2.3.4')

if __name__ == '__main__':
    unittest.main()
