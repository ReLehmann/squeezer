#!/usr/bin/python

# copyright (c) 2020, Matthias Dellweg
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: deb_sync
short_description: Synchronize a deb remote on a pulp server
description:
  - "This module synchronizes a deb remote into a repository."
  - "In check_mode this module assumes, nothing changed upstream."
options:
  remote:
    description:
      - Name of the remote to synchronize
    type: str
    required: true
  repository:
    description:
      - Name of the repository
    type: str
    required: true
  mirror:
    description:
      - Whether to synchronise in mirror mode.
    type: bool
    required: false
    default: false
extends_documentation_fragment:
  - pulp.squeezer.pulp
author:
  - Matthias Dellweg (@mdellweg)
"""

EXAMPLES = r"""
- name: Sync deb remote into repository
  pulp.squeezer.deb_sync:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
    repository: repo_1
    remote: remote_1
  register: sync_result
- name: Report synched repository version
  debug:
    var: sync_result.repository_version
"""

RETURN = r"""
  repository_version:
    description: Repository version after synching
    type: dict
    returned: always
"""


from ansible_collections.pulp.squeezer.plugins.module_utils.pulp import (
    PulpAnsibleModule,
    PulpDebRemote,
    PulpDebRepository,
)


def main():
    with PulpAnsibleModule(
        argument_spec=dict(
            remote=dict(required=True),
            repository=dict(required=True),
            mirror=dict(type="bool", default=False),
        ),
    ) as module:
        remote = PulpDebRemote(module, {"name": module.params["remote"]})
        remote.find(failsafe=False)

        repository = PulpDebRepository(module, {"name": module.params["repository"]})
        repository.find(failsafe=False)

        parameters = {"mirror": module.params["mirror"]}
        repository.process_sync(remote, parameters)


if __name__ == "__main__":
    main()
