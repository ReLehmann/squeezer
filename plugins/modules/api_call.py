#!/usr/bin/python

# copyright (c) 2019, Matthias Dellweg
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: api_call
short_description: TBD
description:
  - "TBD"
options:
  operation_id:
    description: "ID of the openapi operation to perform."
    type: str
    required: true
  parameters:
    description: "Dictionary of (path, query and cookie) parameters to send along with the request."
    type: dict
    required: false
  body:
    description: "JSON representation of the body to send in the request (only POST, PUT and PATCH requests.)"
    type: dict
    required: false
extends_documentation_fragment:
  - pulp.squeezer.pulp.glue
  - pulp.squeezer.pulp
author:
  - Matthias Dellweg (@mdellweg)
"""

EXAMPLES = r"""
- name: Read status from pulp api server
  pulp.squeezer.api_call:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
  register: pulp_result
- name: Report pulp status
  debug:
    var: pulp_result.response
"""

RETURN = r"""
  response:
    description: Pulp api response
    type: dict
    returned: always
"""


from ansible_collections.pulp.squeezer.plugins.module_utils.pulp_glue import PulpAnsibleModule

try:
    from pulp_glue.common.context import NotImplementedFake
except ImportError:
    NotImplementedFake = None


def main():
    with PulpAnsibleModule(
        argument_spec={
            "operation_id": {"required": True},
            "parameters": {"type": "dict"},
            "body": {"type": "dict"},
        },
    ) as module:
        operation_id = module.params["operation_id"]
        parameters = module.params["parameters"]
        body = module.params["body"]
        if module.pulp_ctx.api.operations[operation_id][0].upper() not in ["GET", "HEAD"]:
            module.set_changed()
        try:
            response = module.pulp_ctx.call(operation_id, parameters=parameters, body=body)
        except NotImplementedFake:
            if module.check_mode:
                response = None
        module.set_result("response", response)


if __name__ == "__main__":
    main()
