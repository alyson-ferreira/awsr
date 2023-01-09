"""AWS credential file tool"""

import os
from typing import Iterable, List
from io import StringIO

from awsr import tooling


class Credential:
    """Represents a ini section of the credential file for AWS."""

    properties = [
        "aws_access_key_id",
        "aws_secret_access_key",
        "aws_session_token",
        "profile",
    ]

    def __init__(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        aws_session_token="",
        profile="default",
    ):
        self.profile = profile
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token

    @classmethod
    def from_profile_section(cls, profile_section: str):
        """Converts an credential ini section into an instance.

        Args:
            profile_section: The string with the ini section.
        """
        parts = iter(
            [
                p.strip()
                for p in profile_section.splitlines(keepends=False)
                if p.strip()
            ]
        )
        profile_name = next(parts).strip("[]")
        properties = [tooling.equal_splitter(p) for p in parts]
        arguments = {
            prop[0]: prop[1]
            for prop in properties
            if prop[0].startswith("aws") and prop[0] in Credential.properties
        }
        return cls(profile=profile_name, **arguments)

    def ini_props_dict(self):
        """Returns the ini properties this object represents."""
        return {
            "aws_access_key_id": self.aws_access_key_id,
            "aws_secret_access_key": self.aws_secret_access_key,
            "aws_session_token": self.aws_session_token,
        }

    def __repr__(self):
        return tooling.ini_section(self.ini_props_dict(), self.profile)

    def __str__(self):
        return tooling.ini_section(self.ini_props_dict(), self.profile)


class CredentialFile:
    """Represents the AWS credential file"""

    def __init__(self, path=""):
        self.path = path or get_credentials_path()

    def grab_parts(self):
        """Returns the list of credentials"""
        with open(self.path, "r") as source:
            buffer = StringIO()
            for line in source:
                line = line.strip()
                if line.startswith("["):
                    content = buffer.getvalue()
                    buffer = StringIO()
                    if content:
                        yield content
                if line:
                    buffer.write(f"{line}\n")
            content = buffer.getvalue()
            if content:
                yield content

    def grab_profiles(self) -> List[Credential]:
        """Separates the ini sections and returns a credential instance for
        each section as a list."""
        return [
            Credential.from_profile_section(section)
            for section in self.grab_parts()
        ]

    def write_profiles(self, creds: Iterable[Credential]):
        """Writes the list of credentials to the credential file by
        overwriting.
        """
        with open(self.path, "w") as target:
            target.writelines([f"{cred}\n" for cred in creds])


def override_profile(
    profile: str, replacement_cred: Credential, cred_file=""
) -> str:
    """Write profile replacing the content of the ini section pointed by
    the profile name.

    Args:
        profile: The ini section name.
        replacement_cred: The new credential for fill in profile.
        cred_file: The credential ini file.

    Returns:
        The replaced credential.
    """
    replaced_key = ""
    credfile = CredentialFile(cred_file)
    creds = credfile.grab_profiles()
    for pos, cred in enumerate(creds):
        if cred.profile == profile:
            replaced_key = cred.aws_access_key_id
            del creds[pos]
    creds.append(replacement_cred)
    credfile.write_profiles(creds)
    return replaced_key


def get_credentials_path():
    """Returns the credential path based on the environment."""
    return os.getenv("AWS_SHARED_CREDENTIALS_FILE", "") or os.path.join(
        os.getenv("HOME", os.getenv("USERPROFILE", "")), ".aws", "credentials"
    )
