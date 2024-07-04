#!/usr/bin/python

# copyright (c) 2020, Matthias Dellweg
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: python_sync
short_description: Synchronize a python remote on a pulp server
description:
  - "This module synchronizes a python remote into a repository."
  - "In check_mode this module assumes, nothing changed upstream."
options:
  remote:
    description:
      - Name of the remote to synchronize
    type: str
    required: false
  repository:
    description:
      - Name of the repository
    type: str
    required: true
extends_documentation_fragment:
  - pulp.squeezer.pulp.glue
  - pulp.squeezer.pulp
author:
  - Matthias Dellweg (@mdellweg)
"""

EXAMPLES = r"""
- name: Sync python remote into repository
  pulp.squeezer.python_sync:
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


import traceback

from ansible_collections.pulp.squeezer.plugins.module_utils.pulp_glue import (
    PulpAnsibleModule,
    SqueezerException,
)

try:
    from pulp_glue.python.context import PulpPythonRemoteContext, PulpPythonRepositoryContext

    PULP_CLI_IMPORT_ERR = None
except ImportError:
    PULP_CLI_IMPORT_ERR = traceback.format_exc()


def main():
    with PulpAnsibleModule(
        import_errors=[("pulp-glue", PULP_CLI_IMPORT_ERR)],
        argument_spec=dict(
            remote=dict(required=False),
            repository=dict(required=True),
        ),
    ) as module:
        repository_ctx = PulpPythonRepositoryContext(
            module.pulp_ctx, entity={"name": module.params["repository"]}
        )
        repository = repository_ctx.entity

        payload = {}
        if module.params["remote"] is None:
            if repository["remote"] is None:
                raise SqueezerException(
                    "No remote was specified and none preconfigured on the repository."
                )
        else:
            remote_ctx = PulpPythonRemoteContext(
                module.pulp_ctx, entity={"name": module.params["remote"]}
            )
            payload["remote"] = remote_ctx
        repository_version = repository["latest_version_href"]
        # In check_mode, assume nothing changed
        if not module.check_mode:
            sync_task = repository_ctx.sync(body=payload)

            if sync_task["created_resources"]:
                module.set_changed()
                repository_version = sync_task["created_resources"][0]

        module.set_result("repository_version", repository_version)


if __name__ == "__main__":
    main()
