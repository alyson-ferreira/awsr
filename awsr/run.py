import argparse
from os import getenv
from typing import List
from awsr.credentials import CredentialFile, Credential
from awsr.iam import AccessKey
from awsr.iam import list_keys_from_user
from awsr.iam import create_access_key
from awsr.iam import delete_access_key
from awsr.iam import wait_for_key_avaiability


class Args:
    __slots__ = (
        "user_name",
        "profile",
        "verbose",
        "credential_file",
    )

    def __init__(self):
        self.user_name = ""
        self.profile = getenv("AWS_PROFILE", "default")
        self.verbose = False
        self.credential_file = ""

    @classmethod
    def from_cli(cls):
        args = argparse.ArgumentParser()
        args.add_argument("user_name")
        args.add_argument("-p", "--profile")
        args.add_argument("-c", "--credential-file", dest="credential_file")
        args.add_argument("-v", "--verbose", action="store_true")
        inst = cls()
        args.parse_args(namespace=inst)
        return inst


def delete_inactive_keys(
    user,
    keys: List[AccessKey]
) -> List[AccessKey]:
    inactive_keys = filter(lambda k: k.status == "Inactive", keys)
    for key in inactive_keys:
        delete_access_key(user, key.access_key_id)
    return list(
        filter(lambda k: not k.status == "Inactive", keys)
    )


def override_profile(profile: str,
                     replacement_cred: Credential,
                     cred_file="") -> str:
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


def run():
    args = Args.from_cli()
    user_keys = list_keys_from_user(args.user_name)

    if not user_keys:
        return

    if len(user_keys) == 2:
        user_keys = delete_inactive_keys(args.user_name, user_keys)

    if len(user_keys) == 2:
        user_keys = list(sorted(user_keys, key=lambda k: k.create_date))
        delete_access_key(args.user_name, user_keys[0].access_key_id)
        del user_keys[0]

    old_key = user_keys[0]
    new_key = create_access_key(args.user_name)

    if not wait_for_key_avaiability(new_key):
        delete_access_key(new_key.user_name, new_key.access_key_id)
        return 1

    new_cred = Credential(
        new_key.access_key_id,
        new_key.secret_access_key,
        profile=args.profile
    )

    previous_key = override_profile(args.profile,
                                    new_cred,
                                    cred_file=args.credential_file)

    delete_access_key(old_key.user_name, old_key.access_key_id)

    if args.verbose:
        print(previous_key, new_cred.aws_access_key_id, sep="->")
