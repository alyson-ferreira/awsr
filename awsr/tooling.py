from typing import Callable


def slots_to_dict(o: object) -> dict:
    return dict(map(lambda k: (k, getattr(o, k)), o.__slots__))


def key_value_str_block(d: dict, str_converter: Callable = str) -> str:
    return "\n".join([
        f"{str_converter(k)} = {str_converter(v)}"
        for k, v in d.items()
    ])


def inify_object(o: object, section_name="", section_name_attribute="") -> str:
    if not section_name:
        if section_name_attribute:
            section_name = getattr(o, section_name_attribute)
        else:
            section_name = type(o).__name__

    content: dict = slots_to_dict(o) if hasattr(o, "__slots__") else vars(o)
    return f"[{section_name}]\n{key_value_str_block(content)}"
