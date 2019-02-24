# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import unicode_literals

import unittest

from mo_files import TempDirectory, File
from mo_logs import Log
from mo_threads import Process

import mo_json
from mo_json import json2value, value2json


class TestNSTSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.backup = mo_json.SNAP_TO_BASE_10
        cls.dir = File("tests/resources")
        if (cls.dir / "JSONTestSuite").exists:
            p = Process("clone", ["git", "pull", "origin", "master"], cwd=cls.dir / "JSONTestSuite", debug=True)
            p.join(raise_on_error=True)
        else:
            p = Process("clone", ["git", "clone", "https://github.com/nst/JSONTestSuite.git"], cwd=cls.dir, debug=True)
            p.join(raise_on_error=True)
        mo_json.SNAP_TO_BASE_10 = True

    @classmethod
    def tearDownClass(cls):
        mo_json.SNAP_TO_BASE_10 = cls.backup

    def test_parsing(self):
        fail = False
        children = list((TestNSTSuite.dir / "JSONTestSuite" / "test_parsing").children)

        for file in children:
            bytes = file.read_bytes()
            try:
                content = bytes.decode("utf8")
                output = json2value(content)
                if file.name.startswith("n"):
                    if content in ["[Infinity]", "[-Infinity]", "[NaN]"]:
                        continue  # STILL OK
                    fail = True
                    Log.note("parsing should fail on {{content|quote}}", content=content)
                else:
                    json = value2json(output)
                    Log.note("  result={{json|quote}}\noriginal={{content|quote}}", json=json, content=content)
            except Exception as e:
                if file.name.startswith("y"):
                    fail = True
                    Log.note("parsing should pass on {{content|quote}}", content=bytes)
        if fail:
            Log.error("there are some failures")
        else:
            Log.note("{{num}} files tested", num=len(children))

    def test_transform(self):
        children = list((TestNSTSuite.dir / "JSONTestSuite" / "test_transform").children)

        for file in children:
            bytes = file.read_bytes()
            try:
                content = bytes.decode("utf8")

                output = json2value(content)
                json = value2json(output)

                Log.note("  result={{json|quote}}\noriginal={{content|quote}}", json=json, content=content)
            except Exception as e:
                Log.error("parsing should pass {{file}} on {{content|quote}}", file=file.name, content=bytes, cause=e)
        Log.note("{{num}} files tested", num=len(children))
