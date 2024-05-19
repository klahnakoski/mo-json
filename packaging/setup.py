# encoding: utf-8
# THIS FILE IS AUTOGENERATED!
from setuptools import setup
setup(
    author='Kyle Lahnakoski',
    author_email='kyle@lahnakoski.com',
    classifiers=["Development Status :: 4 - Beta","License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)","Programming Language :: Python :: 3.8","Programming Language :: Python :: 3.9","Topic :: Software Development :: Libraries","Topic :: Software Development :: Libraries :: Python Modules","Programming Language :: Python :: 3.10","Programming Language :: Python :: 3.11","Programming Language :: Python :: 3.12"],
    description='More JSON Tools! ',
    extras_require={"tests":["mo-testing>=8.623.24125","mo-threads>=6.623.24125","pytz>=2024.1","beautifulsoup4>=4.12.3"]},
    install_requires=["hjson","mo-dots==10.632.24139","mo-future==7.584.24095","mo-logs==8.632.24139","mo-times==5.632.24139"],
    license='MPL 2.0',
    long_description={"$concat":["# More JSON Tools",null,null,"[![PyPI Latest Release](https://img.shields.io/pypi/v/mo-json.svg)](https://pypi.org/project/mo-json/)"," [![Build Status](https://github.com/klahnakoski/mo-json/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/klahnakoski/mo-json/actions/workflows/build.yml)"," [![Coverage Status](https://coveralls.io/repos/github/klahnakoski/mo-json/badge.svg?branch=dev)](https://coveralls.io/github/klahnakoski/mo-json?branch=dev)","[![Downloads](https://pepy.tech/badge/mo-json)](https://pepy.tech/project/mo-json)",null,null,"This set of modules provides the following benefits:",null,"* Serialize more datastructures into JSON","* More flexibility  in what's accepted as \"JSON\"","* Iterate over massive JSON easily (`mo_json.stream`)","* Provide a bijection between strictly typed JSON, and dynamic typed JSON.",null,null,"## Recent Changes",null,"* **Version 6.x.x** - Typed encoder no longer encodes to typed multivalues, rather, encodes to array of typed values.  For example, instead of ",null,"      {\"a\": {\"~n~\": [1, 2]}}",null,"  we get ",null,"      {\"a\": {\"~a~\": [{\"~n~\": 1},{\"~n~\": 2}]}} ",null,"## Usage",null,"### Encode using `__json__`",null,"Add a `__json__` method to any class you wish to serialize to JSON. It is incumbent on you to ensure valid JSON is emitted:",null,"    class MyClass(object):","        def __init__(self, a, b):","            self.a = a","            self.b = b",null,"        def __json__(self):","            separator = \"{\"","            for k, v in self.__dict__.items():","                yield separator","                separator = \",\"","                yield value2json(k)+\": \"+value2json(v)","            yield \"}\"",null,"With the `__json__` function defined, you may use the `value2json` function:",null,"    from mo_json import value2json",null,"    result = value2json(MyClass(a=\"name\", b=42))    ",null,null,"### Encode using `__data__`",null,"Add a `__data__` method that will convert your class into some JSON-serializable data structures.  You may find this easier to implement than emitting pure JSON.  **If both `__data__` and `__json__` exist, then `__json__` is used.**   ",null,"    from mo_json import value2json",null,"    class MyClass(object):","        def __init__(self, a, b):","            self.a = a","            self.b = b",null,"        def __data__(self):","            return self.__dict__",null,"    result = value2json(MyClass(a=\"name\", b=42))    ",null,null,"### Decoding",null,"The `json2value` function provides a couple of options",null,"* `flexible` - will be very forgiving of JSON accepted (see [hjson](https://pypi.org/project/hjson/))","* `leaves` - will interpret keys with dots (\"`.`\") as dot-delimited paths",null,null,"```","from mo_json import json2value",null,"result = json2value(","    \"http.headers.referer: http://example.com\", ","    flexible=True, ","    leaves=True",")","assert result=={'http': {'headers': {'referer': 'http://example.com'}}}","```",null,"Notice the lack of quotes in the JSON (hjson) and the deep structure created by the dot-delimited path name",null,"## Running tests",null,"    pip install -r tests/requirements.txt","    set PYTHONPATH=.    ","    python.exe -m unittest discover tests",null,null,"## Module Details",null,"### Method `mo_json.scrub()`",null,"Remove, or convert, a number of objects from a structure that are not JSON-izable. It is faster to `scrub` and use the default (aka c-based) python encoder than it is to use `default` serializer that forces the use of an interpreted python encoder. ",null,"----------------------",null,"### Module `mo_json.stream`",null,"A module that supports queries over very large JSON","strings. The overall objective is to make a large JSON document appear like","a hierarchical database, where arrays of any depth, can be queried like","tables. ",null,null,"#### Limitations",null,"This is not a generic streaming JSON parser. It is only intended to breakdown the top-level array, or object for less memory usage.  ",null,"*  **Array values must be the last object property** - If you query into a ","   nested array, all sibling properties found after that array must be ignored ","   (must not be in the `expected_vars`). The code will raise an exception if","   you can not extract all expected variables.",null,"----------------------",null,"### Method `mo_json.stream.parse()`",null,"Will return an iterator over all objects found in the JSON stream.",null,"**Parameters:**",null,"* **json** - a parameter-less function, when called returns some number of","  bytes from the JSON stream. It can also be a string.","* **path** - a dot-delimited string specifying the path to the nested JSON. Use ","  `\".\"` if your JSON starts with `[`, and is a list.","* **expected_vars** - a list of strings specifying the full property names ","  required (all other properties are ignored)",null,"#### Common Usage",null,"The most common use of `parse()` is to iterate over all the objects in a large, top-level, array:",null,"    parse(json, path=\".\", required_vars=[\".\"]}",null,"For example, given the following JSON: ",null,"    [","        {\"a\": 1},","        {\"a\": 2},","        {\"a\": 3},","        {\"a\": 4}","    ]",null,"returns a generator that provides",null,"    {\"a\": 1}","    {\"a\": 2}","    {\"a\": 3}","    {\"a\": 4}",null,null,"#### Examples",null,"**Simple Iteration**",null,"    json = {\"b\": \"done\", \"a\": [1, 2, 3]}","    parse(json, path=\"a\", required_vars=[\"a\", \"b\"]}",null,"We will iterate through the array found on property `a`, and return both `a` and `b` variables. It will return the following values:",null,"    {\"b\": \"done\", \"a\": 1}","    {\"b\": \"done\", \"a\": 2}","    {\"b\": \"done\", \"a\": 3}",null,null,"**Bad - Property follows array**",null,"The same query, but different JSON with `b` following `a`:",null,"    json = {\"a\": [1, 2, 3], \"b\": \"done\"}","    parse(json, path=\"a\", required_vars=[\"a\", \"b\"]}",null,"Since property `b` follows the array we're iterating over, this will raise an error.",null,"**Good - No need for following properties**",null,"The same JSON, but different query, which does not require `b`:",null,"    json = {\"a\": [1, 2, 3], \"b\": \"done\"}","    parse(json, path=\"a\", required_vars=[\"a\"]}",null,"If we do not require `b`, then streaming will proceed just fine:",null,"    {\"a\": 1}","    {\"a\": 2}","    {\"a\": 3}",null,"**Complex Objects**",null,"This streamer was meant for very long lists of complex objects. Use dot-delimited naming to refer to full name of the property",null,"    json = [{\"a\": {\"b\": 1, \"c\": 2}}, {\"a\": {\"b\": 3, \"c\": 4}}, ...","    parse(json, path=\".\", required_vars=[\"a.c\"])",null,"The dot (`.`) can be used to refer to the top-most array. Notice the structure is maintained, but only includes the required variables.",null,"    {\"a\": {\"c\": 2}}","    {\"a\": {\"c\": 4}}","    ...",null,"**Nested Arrays**",null,"Nested array iteration is meant to mimic a left-join from parent to child table;","as such, it includes every record in the parent. ",null,"    json = [","        {\"o\": 1: \"a\": [{\"b\": 1}: {\"b\": 2}: {\"b\": 3}: {\"b\": 4}]},","        {\"o\": 2: \"a\": {\"b\": 5}},","        {\"o\": 3}","    ]","    parse(json, path=[\".\", \"a\"], required_vars=[\"o\", \"a.b\"])",null,"The `path` parameter can be a list, which is used to indicate which properties","are expected to have an array, and to iterate over them. Please notice if no","array is found, it is treated like a singleton array, and missing arrays still","produce a result.",null,"    {\"o\": 1, \"a\": {\"b\": 1}}","    {\"o\": 1, \"a\": {\"b\": 2}}","    {\"o\": 1, \"a\": {\"b\": 3}}","    {\"o\": 1, \"a\": {\"b\": 4}}","    {\"o\": 2, \"a\": {\"b\": 5}}","    {\"o\": 3}",null,"**Large top-level objects**",null,"Some JSON is a single large object, rather than an array of objects. In these cases, you can use the `items` operator to iterate through all name/value pairs of an object:",null,"    json = {","        \"a\": \"test\",","        \"b\": 2,","        \"c\": [1, 2]","    }","    parse(json, {\"items\": \".\"}, {\"name\", \"value\"})   ",null,"produces an iterator of",null,"    {\"name\": \"a\", \"value\": \"test\"} ","    {\"name\": \"b\", \"value\": 2} ","    {\"name\": \"c\", \"value\": [1,2]} ",null,"----------------------",null,"### Module `typed_encoder`",null,null,"One reason that NoSQL documents stores are wonderful is their schema can automatically expand to accept new properties. Unfortunately, this flexibility is not limitless; A string assigned to property prevents an object being assigned to the same, or visa-versa. This flexibility is under attack by the strict-typing zealots; who, in their self-righteous delusion, believe explicit types are better. They make the lives of humans worse; as we are forced to toil over endless schema modifications.",null,"This module translates JSON documents into \"typed\" form; which allows document containers to store both objects and primitives in the same property. This also enables the storage of values with no containing object! ",null,"The typed JSON has a different form than the original, and queries into the document store must take this into account. This conversion is intended to be hidden behind a query abstraction layer that can understand this format.",null,"#### How it works",null,"There are three main conversions:",null,"1. Primitive values are replaced with single-property objects, where the property name indicates the data type of the value stored:","   ```","   {\"a\": true} -> {\"a\": {\"~b~\": true}} ","   {\"a\": 1   } -> {\"a\": {\"~n~\": 1   }} ","   {\"a\": \"1\" } -> {\"a\": {\"~s~\": \"1\" }}","   ```","2. JSON objects get an additional property, `~e~`, to mark existence. This allows us to query for object existence, and to count the number of objects.","   ```    ","   {\"a\": {}} -> {\"a\": {\"~e~\": 1}, \"~e~\": 1}  ","   ```","3. JSON arrays are contained in a new object, along with `~e~` to count the number of elements in the array:","   ```    ","   {\"a\": [1, 2, 3]} -> {\"a\": {","       \"~e~\": 3, ","       \"~a~\": [","           {\"~n~\": 1},","           {\"~n~\": 2},","           {\"~n~\": 3}","       ]","   }}","   ```","   Note the sum of `a.~e~` works for both objects and arrays; letting us interpret sub-objects as single-value nested object arrays. ",null,"### Function `typed_encode()`",null,"Accepts a `dict`, `list`, or primitive value, and generates the typed JSON that can be inserted into a document store.",null,"### Function `json2typed()`",null,"Converts an existing JSON unicode string and returns the typed JSON unicode string for the same.",null,null,"----------------------",null,"**Update Mar2016** - *PyPy version 5.x appears to have improved C integration to","the point that the C library callbacks are no longer a significant overhead:","This pure Python JSON encoder is no longer faster than a compound C/Python","solution.*",null,"Fast JSON encoder used in `convert.value2json()` when running in Pypy. Run the","[speed test](https://github.com/klahnakoski/mo-json/blob/dev/tests/speedtest_json.py)","to compare with default implementation and ujson",null,null]},
    long_description_content_type='text/markdown',
    name='mo-json',
    packages=["mo_json"],
    url='https://github.com/klahnakoski/mo-json',
    version='6.637.24140'
)