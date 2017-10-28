# More JSON Tools!

This set of modules solves three problems:

* We want to iterate over massive JSON easily (`mo_json.stream`)
* A bijection between strictly typed JSON, and dynamic typed JSON.
* Flexible JSON parser to handle comments, and other forms
* <strike>JSON encoding is slow (`mo_json.encode`)</strike>

## Module `mo_json.stream`

A module that supports queries over very large JSON
strings. The overall objective is to make a large JSON document appear like
a hierarchical database, where arrays of any depth, can be queried like
tables. 


### Limitations

This is not a generic streaming JSON parser. It is only intended to breakdown the top-level array, or object for less memory usage.  

*  **Array values must be the last object property** - If you query into a 
   nested array, all sibling properties found after that array must be ignored 
   (must not be in the `expected_vars`). The code will raise an exception if
   you can not extract all expected variables.

###Function `parse()`

Will return an iterator over all objects found in the JSON stream.

**Parameters:**

* **json** - a parameter-less function, when called returns some number of
  bytes from the JSON stream. It can also be a string.
* **path** - a dot-delimited string specifying the path to the nested JSON. Use 
  `"."` if your JSON starts with `[`, and is a list.
* **expected_vars** - a list of strings specifying the full property names 
  required (all other properties are ignored)

####Examples

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
	parse(json, {"items":"."}, {"name", "value"})   

produces an iterator of

	{"name": "a", "value":"test"} 
	{"name": "b", "value":2} 
	{"name": "c", "value":[1,2]} 


Module `typed_encoder`
----------------------


One reason NoSQL documents stores are wonderful is the fact their schema can automatically expand to accept new properties. Unfortunately, this flexibility is not limitless; A string assigned to property prevents an object being assigned to the same, or visa-versa. This flexibility is under attack by the strict-typing zealots, who, in their self righteous delusion believe explicit types are better, actually make the lives of humans worse; with endless schema modifications.

This module translates JSON documents into "typed" form; which allows document containers to store both objects and primitives in the same property value. This allows storage of values with no containing object!

###How it works

Typed JSON uses `$value` and `$object` properties to markup the original JSON:

* All JSON objects are annotated with `"$object":"."`, which makes querying object existence (especially the empty object) easier.
* All primitive values are replaced with an object with a single `$value` property: So `"value"` gets mapped to `{"$value": "value"}`.

Of course, the typed JSON has a different form than the original, and queries into the documents store must take this into account. Fortunately, the use of typed JSON is intended to be hidden behind a query abstraction layer.


### Function `typed_encode()`

Accepts a `dict`, `list`, or primitive value, and generates the typed JSON that can be inserted into a document store.


### Function `json2typed()`

Converts an existing JSON unicode string and returns the typed JSON unicode string for the same.



---

also see [http://tools.ietf.org/id/draft-pbryan-zyp-json-ref-03.html](http://tools.ietf.org/id/draft-pbryan-zyp-json-ref-03.html)

Module `mo_json.encode`
-----------------------

###Function: `mo_json.encode.json_encoder()`

**Update Mar2016** - *PyPy version 5.x appears to have improved C integration to
the point that the C library callbacks are no longer a significant overhead:
This pure Python JSON encoder is no longer faster than a compound C/Python
solution.*

Fast JSON encoder used in `convert.value2json()` when running in Pypy. Run the
[speedtest](https://github.com/klahnakoski/pyLibrary/blob/dev/tests/speedtest_json.py)
to compare with default implementation and ujson

