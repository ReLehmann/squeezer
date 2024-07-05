#!/usr/bin/python

# copyright (c) 2019, Matthias Dellweg
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: python_publication
short_description: Manage python publications of a pulp api server instance
description:
  - "This performs CRUD operations on python publications in a pulp api server instance."
options:
  repository:
    description:
      - Name of the repository to be published
    type: str
    required: false
  version:
    description:
      - Version number to be published
    type: int
    required: false
extends_documentation_fragment:
  - pulp.squeezer.pulp.entity_state
  - pulp.squeezer.pulp.glue
  - pulp.squeezer.pulp
author:
  - Matthias Dellweg (@mdellweg)
"""

EXAMPLES = r"""
- name: Read list of python publications
  pulp.squeezer.python_publication:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
  register: publication_status
- name: Report pulp python publications
  debug:
    var: publication_status

- name: Create a python publication
  pulp.squeezer.python_publication:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
    repository: my_python_repo
    state: present

- name: Delete a python publication
  pulp.squeezer.python_publication:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
    repository: my_python_repo
    state: absent
"""

RETURN = r"""
  publications:
    description: List of python publications
    type: list
    returned: when no repository is given
  publication:
    description: Python publication details
    type: dict
    returned: when repository is given
"""


import traceback

from ansible_collections.pulp.squeezer.plugins.module_utils.pulp_glue import PulpEntityAnsibleModule

try:
    from pulp_glue.python.context import PulpPythonPublicationContext, PulpPythonRepositoryContext

    PULP_CLI_IMPORT_ERR = None
except ImportError:
    PULP_CLI_IMPORT_ERR = traceback.format_exc()
    PulpPythonPublicationContext = None


def main():
    with PulpEntityAnsibleModule(
        context_class=PulpPythonPublicationContext,
        entity_singular="publication",
        entity_plural="publications",
        import_errors=[("pulp-glue", PULP_CLI_IMPORT_ERR)],
        argument_spec={
            "repository": {},
            "version": {"type": "int"},
        },
        required_if=(
            ["state", "present", ["repository"]],
            ["state", "absent", ["repository"]],
        ),
    ) as module:
        repository_name = module.params["repository"]
        version = module.params["version"]
        desired_attributes = {}

        if repository_name:
            repository_ctx = PulpPythonRepositoryContext(
                module.pulp_ctx, entity={"name": repository_name}
            )
            repository = repository_ctx.entity
            # TODO check if version exists
            if version:
                repository_version_href = repository["versions_href"] + f"{version}/"
            else:
                repository_version_href = repository["latest_version_href"]
            natural_key = {"repository_version": repository_version_href}
        else:
            natural_key = {"repository_version": None}

        module.process(natural_key, desired_attributes)


if __name__ == "__main__":
    main()
