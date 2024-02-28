#!/usr/bin/env python

import json
import os
import re
import sys

import vcr

try:
    from urlparse import parse_qs, urlparse, urlunparse
except ImportError:
    from urllib.parse import parse_qs, urlparse, urlunparse


def safe_method_matcher(r1, r2):
    assert r1.method not in [
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ], "Method {0} not allowed in check_mode".format(r1.method)
    assert r1.method == r2.method


# We need our own json level2 matcher, because, python2 and python3 do not save
# dictionaries in the same order.
# Also multipart bounderies must be ignored.
def amp_body_matcher(r1, r2):
    c1 = r1.headers.get("content-type", "")
    c2 = r2.headers.get("content-type", "")
    body1 = r1.body
    body2 = r2.body
    if body1 is not None and body2 is not None:
        if c1 == "application/json":
            assert c2 == "application/json", "content-type mismatch"
            body1 = json.loads(body1.decode("utf8"))
            body2 = json.loads(body2.decode("utf8"))
            if "search" in body1:
                body1["search"] = ",".join(
                    sorted(re.findall(r'([^=,]*="(?:[^"]|\\")*")', body1["search"]))
                )
            if "search" in body2:
                body2["search"] = ",".join(
                    sorted(re.findall(r'([^=,]*="(?:[^"]|\\")*")', body2["search"]))
                )
        elif c1.startswith("application/x-www-form-urlencoded"):
            assert c2.startswith("application/x-www-form-urlencoded"), "content-type mismatch"
            body1 = parse_qs(body1)
            body2 = parse_qs(body2)
        elif c1.startswith("multipart/form-data"):
            assert c2.startswith("multipart/form-data"), "content-type mismatch"
            boundary1 = re.findall(r"boundary=(\S.*)", c1)[0].encode()
            boundary2 = re.findall(r"boundary=(\S.*)", c2)[0].encode()
            body1 = body1.replace(boundary1, b"TILT")
            body2 = body2.replace(boundary2, b"TILT")
            # Older versions of pulp-glue < 0.23 always send "file" as the filename.
            if b'filename="file"' in body1:
                body2 = re.sub(rb'filename="[^"].*"', b'filename="file"', body2)
    assert body1 == body2, "{body1} == {body2}".format(body1=body1, body2=body2)


def filter_request_uri(request):
    request.uri = urlunparse(urlparse(request.uri)._replace(netloc="pulp.example.org"))
    return request


VCR_PARAMS_FILE = os.environ.get("PAM_TEST_VCR_PARAMS_FILE")

# Remove the name of the wrapper from argv
# (to make it look like the module had been called directly)
sys.argv.pop(0)

if VCR_PARAMS_FILE is None:
    # Run the program as if nothing had happened
    with open(sys.argv[0]) as f:
        code = compile(f.read(), sys.argv[0], "exec")
        exec(code)
else:
    # Run the program wrapped within vcr cassette recorder
    # Load recording parameters from file
    with open(VCR_PARAMS_FILE, "r") as params_file:
        test_params = json.load(params_file)
    cassette_file = "../fixtures/{}-{}.yml".format(test_params["test_name"], test_params["serial"])
    # Increase serial and dump back to file
    test_params["serial"] += 1
    with open(VCR_PARAMS_FILE, "w") as params_file:
        json.dump(test_params, params_file)

    # Call the original python script with vcr-cassette in place
    amp_vcr = vcr.VCR()

    if test_params["check_mode"]:
        amp_vcr.register_matcher("safe_method_matcher", safe_method_matcher)
        method_matcher = "safe_method_matcher"
    else:
        method_matcher = "method"

    amp_vcr.register_matcher("amp_body", amp_body_matcher)

    with amp_vcr.use_cassette(
        cassette_file,
        record_mode=test_params["record_mode"],
        match_on=[method_matcher, "path", "query", "amp_body"],
        filter_headers=["Authorization"],
        before_record_request=filter_request_uri,
    ):
        with open(sys.argv[0]) as f:
            code = compile(f.read(), sys.argv[0], "exec")
            exec(code)
