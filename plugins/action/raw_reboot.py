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
module: raw_reboot

short_description: Module issuing a raw style reboot and wait to come online

version_added: "1.1.0"

description: Module for raw reboots

options:
  reboot_timeout:
    description: Maximum number of seconds to wait for a reboot


'''


EXAMPLES = r'''
- name: raw reboot
  raw_reboot:
    reboot_timeout: 1200
'''


class TimeoutException(Exception):
    pass


class ActionModule(ActionBase):

    def run(self, **kwargs):
        result = super(ActionModule, self).run(kwargs)
        result['failed'] = True
        result['rebooted'] = False

        reboot_timeout = int(self._task.args.get('reboot_timeout', 600))
        end_time = datetime.utcnow() + timedelta(seconds=reboot_timeout)

        # Now reboot and then wait
        self._low_level_execute_command("/sbin/reboot", sudoable=True)
        # Sleep just in case the reboot takes a few seconds
        time.sleep(30)

        while datetime.utcnow() < end_time:
            try:
                self._low_level_execute_command("/usr/bin/whoami", sudoable=True)
                result['failed'] = False
                result['rebooted'] = True
                return result
            except Exception as e:
                # a connection failure is fine here, we are waiting for it to reboot anyway
                # reset it and move on
                if isinstance(e, AnsibleConnectionFailure):
                    try:
                        self._connection.reset()
                    except AnsibleConnectionFailure:
                        pass
                time.sleep(60)

        raise TimeoutException("Timed out waiting for the host to reboot timeout seconds {timeout}".format(timeout=reboot_timeout))
