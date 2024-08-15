import json


def decode_unicode_in_json(input_file: str, output_file: str):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    def decode_dict(d):
        if isinstance(d, dict):
            return {k: decode_dict(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [decode_dict(i) for i in d]
        elif isinstance(d, str):
            return d.encode('utf-8').decode('unicode_escape')
        else:
            return d

    decoded_data = decode_dict(data)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(decoded_data, f, ensure_ascii=False, indent=2)


# Usage
decode_unicode_in_json('D:\\projects\\PycharmProjects\\ChatKG\\app\\core\\result.json', 'decoded_result.json')