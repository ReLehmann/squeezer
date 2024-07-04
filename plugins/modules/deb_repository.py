#!/usr/bin/python

# copyright (c) 2020, Matthias Dellweg
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: deb_repository
short_description: Manage deb repositories of a pulp api server instance
description:
  - "This performs CRUD operations on deb repositories in a pulp api server instance."
options:
  name:
    description:
      - Name of the repository to query or manipulate
    type: str
  description:
    description:
      - Description of the repository
    type: str
extends_documentation_fragment:
  - pulp.squeezer.pulp
  - pulp.squeezer.pulp.entity_state
author:
  - Matthias Dellweg (@mdellweg)
"""

EXAMPLES = r"""
- name: Read list of deb repositories from pulp api server
  pulp.squeezer.deb_repository:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
  register: repo_status
- name: Report pulp deb repositories
  debug:
    var: repo_status

- name: Create a deb repository
  pulp.squeezer.deb_repository:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
    name: new_repo
    description: A brand new repository with a description
    state: present

- name: Delete a deb repository
  pulp.squeezer.deb_repository:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
    name: new_repo
    state: absent
"""

RETURN = r"""
  repositories:
    description: List of deb repositories
    type: list
    returned: when no name is given
  repository:
    description: Deb repository details
    type: dict
    returned: when name is given
"""


from ansible_collections.pulp.squeezer.plugins.module_utils.pulp import (
    PulpDebRepository,
    PulpEntityAnsibleModule,
)


def main():
    with PulpEntityAnsibleModule(
        argument_spec=dict(
            name=dict(),
            description=dict(),
        ),
        required_if=[("state", "present", ["name"]), ("state", "absent", ["name"])],
    ) as module:
        natural_key = {"name": module.params["name"]}
        desired_attributes = {}
        if module.params["description"] is not None:
            # In case of an empty string we nullify the description
            desired_attributes["description"] = module.params["description"] or None

        PulpDebRepository(module, natural_key, desired_attributes).process()


if __name__ == "__main__":
    main()
