"""Helpers"""

from typing import Tuple


def key_value_str_block(content: dict) -> str:
    """Converts a dictionary to a string representation suitable for ini files.

    Args:
        d: The dictionary to be processed.

    Returns:
        A string in a key value format using equal sign and new lines to
        separate pairs.
    """
    return "\n".join([f"{k} = {v}" for k, v in content.items()])


def ini_section(props: dict, section_name="", section_name_prop="") -> str:
    """Creates a ini section.

    Args:
        props: The dictionary for ini properties.
        section_name: The ini section name.
        section_name_prop: The attribute of the object that can be used
                                for section name
    Returns:
        A ini section representing the object
    """
    if not section_name:
        if section_name_prop:
            section_name = props.get(section_name_prop)
        else:
            section_name = "default"

    content: str = key_value_str_block(props)
    return f"[{section_name}]\n{content}"


def equal_splitter(content: str) -> Tuple[str, str]:
    """Gets the key before the equal sign and the value after, then returns
    them as a string tuple.

    Args:
        content: The string to be broken into a tuple

    Returns:
        String tuple container key and value
    """
    pos = content.index("=")
    return (
        content[:pos].strip(),
        content[pos + 1 :].strip(),
    )
