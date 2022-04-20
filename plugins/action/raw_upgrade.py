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

import time

from datetime import datetime, timedelta

from ansible.errors import AnsibleConnectionFailure
from ansible.plugins.action import ActionBase


DOCUMENTATION = r'''
---
module: raw_upgrade

short_description: Module issuing a raw style upgrade of firmwares

version_added: "1.1.0"

description: Module for raw upgrades

options:
  retries:
    description: Maximum number of retries
  delay:
    description: Number of seconds to wait between retries


'''


EXAMPLES = r'''
- name: raw upgrade
  raw_upgrade:
    retries: 100
    delay: 60
'''


class FailedActivationException(Exception):
    pass


class UnfinishedActivationException(Exception):
    pass


ACTIVATE_LINE = "busctl set-property xyz.openbmc_project.Software.BMC.Updater /xyz/openbmc_project/software/{} xyz.openbmc_project.Software.Activation RequestedActivation s xyz.openbmc_project.Software.Activation.RequestedActivations.Active"

VERIFY_LINE = "busctl get-property xyz.openbmc_project.Software.BMC.Updater /xyz/openbmc_project/software/{} xyz.openbmc_project.Software.Activation Activation"


class ActionModule(ActionBase):

    def run(self, **kwargs):
        result = super(ActionModule, self).run(kwargs)
        failed = False
        active = False

        retries = int(self._task.args.get('retries', 100))
        delay = int(self._task.args.get('delay', 60))
        current_try = 0

        image_lines = self._low_level_execute_command("ls --color=none -t /tmp/images/")['stdout_lines']
        if len(image_lines) > 1:
            raise FailedActivationException("More than one file is present in /tmp/images")
        image_name = image_lines[0]

        self._low_level_execute_command(ACTIVATE_LINE.format(image_name))

        while current_try < retries:
            verify_out = self._low_level_execute_command(VERIFY_LINE.format(image_name))['stdout']

            if "Activation.Activations.Active" in verify_out:
                active = True
                break
            if "Activation.Activations.Failed" in verify_out:
                failed = True
                break
            current_try += 1
            time.sleep(delay)

        if failed:
            raise FailedActivationException("Activation of firmware has failed")
        if not active:
            raise UnfinishedActivationException("Activation of firmware timed out and stayed in Activating state")

        result['active'] = active
        return result
