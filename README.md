# More JSON Tools


[![PyPI Latest Release](https://img.shields.io/pypi/v/mo-json.svg)](https://pypi.org/project/mo-json/)
 [![Build Status](https://github.com/klahnakoski/mo-json/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/klahnakoski/mo-json/actions/workflows/build.yml)
 [![Coverage Status](https://coveralls.io/repos/github/klahnakoski/mo-json/badge.svg?branch=dev)](https://coveralls.io/github/klahnakoski/mo-json?branch=dev)
[![Downloads](https://pepy.tech/badge/mo-json)](https://pepy.tech/project/mo-json)


This set of modules provides the following benefits:

* Serialize more datastructures into JSON
* More flexibility  in what's accepted as "JSON"
* Iterate over massive JSON easily (`mo_json.stream`)
* Provide a bijection between strictly typed JSON, and dynamic typed JSON.


## Recent Changes

* **Version 6.x.x** - Typed encoder no longer encodes to typed multivalues, rather, encodes to array of typed values.  For example, instead of 

      {"a": {"~n~": [1, 2]}}

  we get 
      
      {"a": {"~a~": [{"~n~": 1},{"~n~": 2}]}} 

## Usage

### Encode using `__json__`

Add a `__json__` method to any class you wish to serialize to JSON. It is incumbent on you to ensure valid JSON is emitted:

    class MyClass(object):
        def __init__(self, a, b):
            self.a = a
            self.b = b

        def __json__(self):
            separator = "{"
            for k, v in self.__dict__.items():
                yield separator
                separator = ","
                yield value2json(k)+": "+value2json(v)
            yield "}"

With the `__json__` function defined, you may use the `value2json` function:

    from mo_json import value2json
    
    result = value2json(MyClass(a="name", b=42))    


### Encode using `__data__`

Add a `__data__` method that will convert your class into some JSON-serializable data structures.  You may find this easier to implement than emitting pure JSON.  **If both `__data__` and `__json__` exist, then `__json__` is used.**   

    from mo_json import value2json

    class MyClass(object):
        def __init__(self, a, b):
            self.a = a
            self.b = b

        def __data__(self):
            return self.__dict__
   
    result = value2json(MyClass(a="name", b=42))    


### Decoding

The `json2value` function provides a couple of options

* `flexible` - will be very forgiving of JSON accepted (see [hjson](https://pypi.org/project/hjson/))
* `leaves` - will interpret keys with dots ("`.`") as dot-delimited paths


```
from mo_json import json2value

result = json2value(
    "http.headers.referer: http://example.com", 
    flexible=True, 
    leaves=True
)
assert result=={'http': {'headers': {'referer': 'http://example.com'}}}
```
 
Notice the lack of quotes in the JSON (hjson) and the deep structure created by the dot-delimited path name

## Running tests

    pip install -r tests/requirements.txt
    set PYTHONPATH=.    
    python.exe -m unittest discover tests


## Module Details

### Method `mo_json.scrub()`

Remove, or convert, a number of objects from a structure that are not JSON-izable. It is faster to `scrub` and use the default (aka c-based) python encoder than it is to use `default` serializer that forces the use of an interpreted python encoder. 

----------------------

### Module `mo_json.stream`

A module that supports queries over very large JSON
strings. The overall objective is to make a large JSON document appear like
a hierarchical database, where arrays of any depth, can be queried like
tables. 


#### Limitations

This is not a generic streaming JSON parser. It is only intended to breakdown the top-level array, or object for less memory usage.  

*  **Array values must be the last object property** - If you query into a 
   nested array, all sibling properties found after that array must be ignored 
   (must not be in the `expected_vars`). The code will raise an exception if
   you can not extract all expected variables.

----------------------

### Method `mo_json.stream.parse()`

Will return an iterator over all objects found in the JSON stream.

**Parameters:**

* **json** - a parameter-less function, when called returns some number of
  bytes from the JSON stream. It can also be a string.
* **path** - a dot-delimited string specifying the path to the nested JSON. Use 
  `"."` if your JSON starts with `[`, and is a list.
* **expected_vars** - a list of strings specifying the full property names 
  required (all other properties are ignored)

#### Common Usage

The most common use of `parse()` is to iterate over all the objects in a large, top-level, array:

    parse(json, path=".", required_vars=["."]}

For example, given the following JSON: 

    [
        {"a": 1},
        {"a": 2},
        {"a": 3},
        {"a": 4}
    ]

returns a generator that provides

    {"a": 1}
    {"a": 2}
    {"a": 3}
    {"a": 4}


#### Examples

**Simple Iteration**

    json = {"b": "done", "a": [1, 2, 3]}
    parse(json, path="a", required_vars=["a", "b"]}

We will iterate through the array found on property `a`, and return both `a` and `b` variables. It will return the following values:

    {"b": "done", "a": 1}
    {"b": "done", "a": 2}
    {"b": "done", "a": 3}


**Bad - Property follows array**

The same query, but different JSON with `b` following `a`:

    json = {"a": [1, 2, 3], "b": "done"}
    parse(json, path="a", required_vars=["a", "b"]}

Since property `b` follows the array we're iterating over, this will raise an error.

**Good - No need for following properties**

The same JSON, but different query, which does not require `b`:

    json = {"a": [1, 2, 3], "b": "done"}
    parse(json, path="a", required_vars=["a"]}

If we do not require `b`, then streaming will proceed just fine:

    {"a": 1}
    {"a": 2}
    {"a": 3}

**Complex Objects**

This streamer was meant for very long lists of complex objects. Use dot-delimited naming to refer to full name of the property

    json = [{"a": {"b": 1, "c": 2}}, {"a": {"b": 3, "c": 4}}, ...
    parse(json, path=".", required_vars=["a.c"])

The dot (`.`) can be used to refer to the top-most array. Notice the structure is maintained, but only includes the required variables.

    {"a": {"c": 2}}
    {"a": {"c": 4}}
    ...

**Nested Arrays**

Nested array iteration is meant to mimic a left-join from parent to child table;
as such, it includes every record in the parent. 

    json = [
        {"o": 1: "a": [{"b": 1}: {"b": 2}: {"b": 3}: {"b": 4}]},
        {"o": 2: "a": {"b": 5}},
        {"o": 3}
    ]
    parse(json, path=[".", "a"], required_vars=["o", "a.b"])

The `path` parameter can be a list, which is used to indicate which properties
are expected to have an array, and to iterate over them. Please notice if no
array is found, it is treated like a singleton array, and missing arrays still
produce a result.

    {"o": 1, "a": {"b": 1}}
    {"o": 1, "a": {"b": 2}}
    {"o": 1, "a": {"b": 3}}
    {"o": 1, "a": {"b": 4}}
    {"o": 2, "a": {"b": 5}}
    {"o": 3}

**Large top-level objects**

Some JSON is a single large object, rather than an array of objects. In these cases, you can use the `items` operator to iterate through all name/value pairs of an object:

    json = {
        "a": "test",
        "b": 2,
        "c": [1, 2]
    }
    parse(json, {"items": "."}, {"name", "value"})   

produces an iterator of

    {"name": "a", "value": "test"} 
    {"name": "b", "value": 2} 
    {"name": "c", "value": [1,2]} 

----------------------

### Module `typed_encoder`


One reason that NoSQL documents stores are wonderful is their schema can automatically expand to accept new properties. Unfortunately, this flexibility is not limitless; A string assigned to property prevents an object being assigned to the same, or visa-versa. This flexibility is under attack by the strict-typing zealots; who, in their self-righteous delusion, believe explicit types are better. They make the lives of humans worse; as we are forced to toil over endless schema modifications.

This module translates JSON documents into "typed" form; which allows document containers to store both objects and primitives in the same property. This also enables the storage of values with no containing object! 

The typed JSON has a different form than the original, and queries into the document store must take this into account. This conversion is intended to be hidden behind a query abstraction layer that can understand this format.

#### How it works

There are three main conversions:

1. Primitive values are replaced with single-property objects, where the property name indicates the data type of the value stored:
   ```
   {"a": true} -> {"a": {"~b~": true}} 
   {"a": 1   } -> {"a": {"~n~": 1   }} 
   {"a": "1" } -> {"a": {"~s~": "1" }}
   ```
2. JSON objects get an additional property, `~e~`, to mark existence. This allows us to query for object existence, and to count the number of objects.
   ```    
   {"a": {}} -> {"a": {"~e~": 1}, "~e~": 1}  
   ```
3. JSON arrays are contained in a new object, along with `~e~` to count the number of elements in the array:
   ```    
   {"a": [1, 2, 3]} -> {"a": {
       "~e~": 3, 
       "~a~": [
           {"~n~": 1},
           {"~n~": 2},
           {"~n~": 3}
       ]
   }}
   ```
   Note the sum of `a.~e~` works for both objects and arrays; letting us interpret sub-objects as single-value nested object arrays. 

### Function `typed_encode()`

Accepts a `dict`, `list`, or primitive value, and generates the typed JSON that can be inserted into a document store.

### Function `json2typed()`

Converts an existing JSON unicode string and returns the typed JSON unicode string for the same.


----------------------

**Update Mar2016** - *PyPy version 5.x appears to have improved C integration to
the point that the C library callbacks are no longer a significant overhead:
This pure Python JSON encoder is no longer faster than a compound C/Python
solution.*

Fast JSON encoder used in `convert.value2json()` when running in Pypy. Run the
[speed test](https://github.com/klahnakoski/mo-json/blob/dev/tests/speedtest_json.py)
to compare with default implementation and ujson

