# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#

import datetime
import unittest

from mo_dots import wrap

from mo_json import value2json, quote
from mo_json.typed_encoder import EXISTS_KEY, NUMBER_KEY, STRING_KEY, BOOLEAN_KEY, ARRAY_KEY, INTEGER_KEY, detype
from mo_json.typed_encoder import encode as typed_encode
from mo_json.typed_object import entype


class TestJSON(unittest.TestCase):
    def test_date(self):
        value = {"test": datetime.date(2013, 11, 13)}
        test1 = typed_encode(value)
        expected = f'{{"test":{{{quote(NUMBER_KEY)}:1384300800}},{quote(EXISTS_KEY)}:1}}'
        self.assertEqual(test1, expected)

    def test_unicode1(self):
        value = {
            "comment": (
                "Open all links in the current tab, except the pages opened from external apps â€” open these ones in"
                " new windows"
            )
        }
        test1 = typed_encode(value)
        expected = (
            f'{{"comment":{{{quote(STRING_KEY)}:"Open all links in the current tab, except the pages opened from external apps â€” open these ones in new windows"}},{quote(EXISTS_KEY)}:1}}'
        )
        self.assertEqual(test1, expected)

    def test_unicode2(self):
        value = {"comment": "testing accented char àáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ"}
        test1 = typed_encode(value)
        expected = (
            f'{{"comment":{{{quote(STRING_KEY)}:"testing accented char àáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ"}},{quote(EXISTS_KEY)}:1}}'
        )
        self.assertEqual(test1, expected)

    def test_unicode3(self):
        value = {"comment": "testing accented char ŕáâăäĺćçčéęëěíîďđńňóôőö÷řůúűüýţ˙"}
        test1 = typed_encode(value)
        expected = (
            f'{{"comment":{{{quote(STRING_KEY)}:"testing accented char ŕáâăäĺćçčéęëěíîďđńňóôőö÷řůúűüýţ˙"}},{quote(EXISTS_KEY)}:1}}'
        )
        self.assertEqual(test1, expected)

    def test_double(self):
        value = {"value": 5.2025595183536973e-07}
        test1 = typed_encode(value)
        expected = f'{{"value":{{{quote(NUMBER_KEY)}:5.202559518353697e-7}},{quote(EXISTS_KEY)}:1}}'
        self.assertEqual(test1, expected)

    def test_empty_list(self):
        value = {"value": []}
        test1 = typed_encode(value)
        expected = f'{{"value":{{{quote(EXISTS_KEY)}:0}},{quote(EXISTS_KEY)}:1}}'
        self.assertEqual(test1, expected)

    def test_nested(self):
        value = {"a": {}, "b": {}}
        test1 = typed_encode(value)
        expected = f'{{"a":{{{quote(EXISTS_KEY)}:1}},"b":{{{quote(EXISTS_KEY)}:1}},{quote(EXISTS_KEY)}:1}}'
        self.assertEqual(test1, expected)

    def test_list_of_objects(self):
        value = {"a": [{}, "b"]}
        test1 = typed_encode(value)
        expected = (
            f'{{"a":{{{quote(ARRAY_KEY)}:[{{{quote(EXISTS_KEY)}:1}},{{{quote(STRING_KEY)}:"b"}}]}},{quote(EXISTS_KEY)}:1}}'
        )
        self.assertEqual(test1, expected)

    def test_empty_list_value(self):
        value = []
        test1 = typed_encode(value)
        expected = f"{{{quote(EXISTS_KEY)}:0}}"
        self.assertEqual(test1, expected)

    def test_list_value(self):
        value = [42]
        test1 = typed_encode(value)
        expected = f"{{{quote(INTEGER_KEY)}:42}}"
        self.assertEqual(test1, expected)

    def test_list_i(self):
        value = {"value": [23, 42]}
        test1 = typed_encode(value)
        expected = f'{{"value":{{{quote(INTEGER_KEY)}:[23,42]}},{quote(EXISTS_KEY)}:1}}'
        self.assertEqual(test1, expected)

    def test_list_n(self):
        value = {"value": [23.5, 42]}
        test1 = typed_encode(value)
        expected = f'{{"value":[{{{quote(NUMBER_KEY)}:23.5}},{{{quote(NUMBER_KEY)}:42}}],{quote(EXISTS_KEY)}:1}}'
        self.assertEqual(test1, expected)

    def test_number_value(self):
        value = 42
        test1 = typed_encode(value)
        expected = f"{{{quote(NUMBER_KEY)}:42}}"
        self.assertEqual(test1, expected)
        self.assertEqual(expected, test1)

    def test_empty_string_value(self):
        value = ""
        test1 = typed_encode(value)
        expected = f'{{{quote(STRING_KEY)}:""}}'
        self.assertEqual(test1, expected)

    def test_string_value(self):
        value = "42"
        test1 = typed_encode(value)
        expected = f'{{{quote(STRING_KEY)}:"42"}}'
        self.assertEqual(test1, expected)

    def test_escaped_string_value(self):
        value = '"'
        test1 = typed_encode(value)
        expected = f'{{{quote(STRING_KEY)}:"\\""}}'
        self.assertEqual(test1, expected)

    def test_bad_key(self):
        test = {24: "value"}
        self.assertRaises(Exception, typed_encode, *[test])

    def test_false(self):
        value = False
        test1 = typed_encode(value)
        expected = f"{{{quote(BOOLEAN_KEY)}:false}}"
        self.assertEqual(test1, expected)

    def test_true(self):
        value = True
        test1 = typed_encode(value)
        expected = f"{{{quote(BOOLEAN_KEY)}:true}}"
        self.assertEqual(test1, expected)

    def test_null(self):
        def encode_null():
            value = None
            typed_encode(value)

        self.assertRaises(Exception, encode_null)

    def test_empty_dict(self):
        value = wrap({"match_all": wrap({})})
        test1 = typed_encode(value)
        expected = f'{{"match_all":{{{quote(EXISTS_KEY)}:1}},{quote(EXISTS_KEY)}:1}}'
        self.assertEqual(test1, expected)

    def test_complex_object(self):
        value = wrap({"s": 0, "r": 5})
        test1 = typed_encode(value)
        expected = f'{{"r":{{{quote(NUMBER_KEY)}:5}},"s":{{{quote(NUMBER_KEY)}:0}},{quote(EXISTS_KEY)}:1}}'
        self.assertEqual(test1, expected)

    def test_empty_list1(self):
        value = wrap({"a": []})
        test1 = typed_encode(value)
        expected = f"{{{quote(EXISTS_KEY)}:1}}"
        self.assertEqual(test1, expected)

    def test_empty_list2(self):
        value = wrap({"a": [], "b": 1})
        test1 = typed_encode(value)
        expected = f'{{"b":{{{quote(NUMBER_KEY)}:1}},{quote(EXISTS_KEY)}:1}}'
        self.assertEqual(test1, expected)

    def test_empty_object(self):
        typed = {EXISTS_KEY: 1}
        test = detype(typed)

        self.assertIsInstance(test, dict)
        self.assertEqual(len(test), 0)

    def test_empty_object_in_list(self):
        value = wrap({"a": [{"b": {}}]})

        test = typed_encode(value)
        expected = f'{{"a":{{"b":{{{quote(EXISTS_KEY)}:1}},{quote(EXISTS_KEY)}:1}},{quote(EXISTS_KEY)}:1}}'
        self.assertEqual(test, expected)

    def test_null_object_in_list(self):
        value = wrap({"a": [{"b": None}]})

        test = typed_encode(value)
        expected = f'{{"a":{{{quote(EXISTS_KEY)}:1}},{quote(EXISTS_KEY)}:1}}'
        self.assertEqual(test, expected)

    def test_singlton_array_of_array_decoded(self):
        typed = {ARRAY_KEY: [{ARRAY_KEY: [{"a": 1}]}]}
        result = detype(typed)
        expected = [[{"a": 1}]]
        self.assertEqual(result, expected)

    def test_encode_typed_json(self):
        typed = entype({"test": [{"a": 1, "b": 2.1}, {"a": "3", "b": 4}]})
        result = value2json(typed)
        expected = value2json({"test": {ARRAY_KEY: [
            {"a": {INTEGER_KEY: 1}, "b": {NUMBER_KEY: 2.1}},
            {"a": {STRING_KEY: "3"}, "b": {INTEGER_KEY: 4}},
        ]}})
        self.assertEqual(result, expected)
