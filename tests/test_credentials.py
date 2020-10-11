from awsr.credentials import Credential, CredentialFormatter, CredentialFile
from os import remove
CREDENTIAL_FILE = "/tmp/_awsr_test.ini"

PROFILE_ROLE = """[test]
aws_access_key_id = abc
aws_secret_access_key = def
aws_session_token =  123
"""

PROFILE_AK = """[test2]
aws_access_key_id = fed
aws_secret_access_key = cba
"""

CREDENTIAL_FILE_CONTENT = f"\n\n{PROFILE_ROLE}\n  \n{PROFILE_AK}\n"


def test_profile_required_values():
    credential_values = "\n".join((
        "aws_access_key_id = key",
        "aws_secret_access_key = secret",
    ))
    credential = Credential("key", "secret")
    assert CredentialFormatter.get_profile_values(
        credential
    ) == credential_values


def test_profile_role_values():
    credential_values = "\n".join((
        "aws_access_key_id = key",
        "aws_secret_access_key = secret",
        "aws_session_token = token"
    ))
    credential = Credential("key", "secret", "token")
    assert CredentialFormatter.get_profile_values(
        credential
    ) == credential_values


def test_grab_parts():
    with open(CREDENTIAL_FILE, "w") as temp:
        temp.write(CREDENTIAL_FILE_CONTENT)

    cred_file = CredentialFile(CREDENTIAL_FILE)
    profiles = [profile for profile in cred_file.grab_parts()]
    assert profiles[0] == PROFILE_ROLE
    assert profiles[1] == PROFILE_AK
    remove(CREDENTIAL_FILE)


def test_grab_profiles():
    with open(CREDENTIAL_FILE, "w") as temp:
        temp.write(CREDENTIAL_FILE_CONTENT)

    cred_file = CredentialFile(CREDENTIAL_FILE)
    creds = [cred for cred in cred_file.grab_profiles()]
    remove(CREDENTIAL_FILE)
    assert creds[0].aws_session_token == "123"
    assert creds[1].aws_access_key_id == "fed"
    assert not creds[1].aws_session_token
