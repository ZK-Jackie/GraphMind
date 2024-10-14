test_dict = {
    "hello": "world",
    "foo": "bar"
}

test_dict2 = {"foo": "bar2"}
test_dict2.update(test_dict)
print(test_dict2)