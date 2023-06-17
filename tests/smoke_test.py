from mo_json import value2json

from mo_json.typed_object import entype

result = entype({"test": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]})
print(value2json(result))
