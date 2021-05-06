from awsr.credentials import CredentialFile

CREDENTIAL_FILE_SUFFIX = "_awsr_test.ini"

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


def test_grab_profiles(tmp_path):
    credential_file = tmp_path / CREDENTIAL_FILE_SUFFIX

    with credential_file.open("w") as temp:
        temp.write(CREDENTIAL_FILE_CONTENT)

    cred_file = CredentialFile(str(credential_file))
    creds = [cred for cred in cred_file.grab_profiles()]
    assert creds[0].aws_session_token == "123"
    assert creds[1].aws_access_key_id == "fed"
    assert not creds[1].aws_session_token
