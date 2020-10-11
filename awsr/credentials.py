from os import getenv
from os import path
from typing import Tuple, Iterable, List
from io import StringIO


def get_credentials_path():
    return (
        getenv("AWS_SHARED_CREDENTIALS_FILE", "") or
        path.join(getenv("HOME", getenv("USERPROFILE", "")),
                  ".aws",
                  "credentials")
    )


def equal_splitter(content: str) -> Tuple[str, str]:
    pos = content.index('=')
    return (content[:pos].strip(), content[pos + 1:].strip(),)


class Credential:
    __slots__ = (
        "profile",
        "aws_access_key_id",
        "aws_secret_access_key",
        "aws_session_token",
    )

    def __init__(self,
                 aws_access_key_id,
                 aws_secret_access_key,
                 aws_session_token="",
                 profile="default"):
        self.profile = profile
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token

    @classmethod
    def from_profile_section(cls, profile_section: str):
        parts = filter(
            lambda p: p.strip(),
            profile_section.splitlines(keepends=False)
        )
        profile_name = next(parts).strip().strip("[]")
        kvs = map(equal_splitter, parts)
        arguments = dict(filter(
            lambda kv: (
                kv[0].startswith("aws") and
                kv[0] in Credential.__slots__
            ),
            kvs
        ))
        return cls(profile=profile_name, **arguments)

    def __repr__(self):
        return CredentialFormatter.get_profile(self, self.profile)

    def __str__(self):
        return CredentialFormatter.get_profile(self, self.profile)


class CredentialFile:
    __slots__ = (
        "path",
    )

    def __init__(self, path=""):
        self.path = path or get_credentials_path()

    def grab_parts(self):
        with open(self.path, "r") as origin:
            buffer = StringIO()
            for line in origin.readlines():
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
        return [
            Credential.from_profile_section(section)
            for section in self.grab_parts()
        ]

    def write_profiles(self, creds: Iterable[Credential]):
        with open(self.path, "w") as target:
            target.writelines([f"{cred}\n" for cred in creds])


class CredentialFormatter:

    @staticmethod
    def get_profile_values(cred: Credential):
        attributes = cred.__slots__
        aws_props = filter(
            lambda a: a.startswith("aws_"),
            attributes
        )
        aws_props = map(
            lambda a: (a, getattr(cred, a),),
            aws_props
        )
        return "\n".join([
            f"{a[0]} = {a[1]}"
            for a in aws_props
            if a[1]
        ])

    @staticmethod
    def get_profile(cred: Credential, name="default"):
        return (
            f"[{name}]\n" +
            f"{CredentialFormatter.get_profile_values(cred)}\n"
        )
