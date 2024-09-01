#!/usr/bin/python

# copyright (c) 2020, Matthias Dellweg
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: task
short_description: Manage tasks of a pulp api server instance
description:
  - "This performs list, show and cancel operations on tasks in a pulp server."
options:
  pulp_href:
    description:
      - Pulp reference of the task to query or manipulate
    type: str
  state:
    description:
      - Desired state of the task.
    type: str
    choices:
      - absent
      - canceled
      - completed
extends_documentation_fragment:
  - pulp.squeezer.pulp.glue
  - pulp.squeezer.pulp
author:
  - Matthias Dellweg (@mdellweg)
"""

EXAMPLES = r"""
- name: Read list of tasks from pulp server
  pulp.squeezer.task:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
  register: task_summary
- name: Report pulp tasks
  debug:
    var: task_summary
"""

RETURN = r"""
  tasks:
    description: List of tasks
    type: list
    returned: when no id is given
  task:
    description: Task details
    type: dict
    returned: when id is given
"""


import traceback

from ansible_collections.pulp.squeezer.plugins.module_utils.pulp_glue import (
    PulpEntityAnsibleModule,
    SqueezerException,
)

try:
    from pulp_glue.common.context import PulpEntityNotFound
    from pulp_glue.core.context import PulpTaskContext

    PULP_CLI_IMPORT_ERR = None
except ImportError:
    PULP_CLI_IMPORT_ERR = traceback.format_exc()
    PulpTaskContext = None


class PulpTaskAnsibleModule(PulpEntityAnsibleModule):
    def process_special(self, desired_attributes, defaults=None):
        if self.state in ["canceled", "completed"]:
            try:
                entity = self.context.entity
            except PulpEntityNotFound:
                raise SqueezerException("Task not found.")
            if entity["state"] in ["waiting", "running", "canceling"]:
                if not self.check_mode:
                    if self.state == "canceled":
                        entity = self.context.cancel()
                    else:
                        entity = self.pulp_ctx.wait_for_task(entity)
                else:
                    # Fake it
                    entity["state"] = self.state
                self.set_changed()
            return entity
        return super().process_special(entity, desired_attributes, defaults)


def main():
    with PulpTaskAnsibleModule(
        context_class=PulpTaskContext,
        entity_singular="task",
        entity_plural="tasks",
        import_errors=[("pulp-glue", PULP_CLI_IMPORT_ERR)],
        argument_spec={
            "pulp_href": {},
            "state": {
                "choices": ["absent", "canceled", "completed"],
            },
        },
        required_if=[
            ("state", "absent", ["pulp_href"]),
            ("state", "canceled", ["pulp_href"]),
            ("state", "completed", ["pulp_href"]),
        ],
    ) as module:
        natural_key = {"pulp_href": module.params["pulp_href"]}
        desired_attributes = {}

        module.process(natural_key, desired_attributes)


if __name__ == "__main__":
    main()
