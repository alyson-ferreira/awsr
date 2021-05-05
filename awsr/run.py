"""Entrypoint"""

import argparse
import os

import boto3

from awsr import credentials
from awsr import iam


class Args:
    """Arguments for the application"""

    def __init__(self):
        self.user_name = ""
        self.profile = os.getenv("AWS_PROFILE", "default")
        self.verbose = False
        self.credential_file = ""

    @classmethod
    def from_cli(cls):
        """Create instance using values passed as arguments to the CLI"""
        parser = argparse.ArgumentParser()
        parser.add_argument("user_name")
        parser.add_argument("-p", "--profile")
        parser.add_argument("-c", "--credential-file", dest="credential_file")
        parser.add_argument("-v", "--verbose", action="store_true")
        args = cls()
        parser.parse_args(namespace=args)
        return args


def run():
    """Entrypoint CLI"""
    args = Args.from_cli()
    iam_client = boto3.client("iam")
    user_keys = iam.list_keys_from_user(iam_client, args.user_name)

    if not user_keys:
        return 0

    user_keys = iam.delete_inactive_keys(iam_client, args.user_name, user_keys)

    if len(user_keys) == 2:
        user_keys = iam.delete_oldest_key(
            iam_client, args.user_name, user_keys
        )
    old_key = user_keys[0]
    new_key = iam.create_access_key(iam_client, args.user_name)

    if not iam.wait_for_key_avaiability(new_key):
        iam_client.delete_access_key(
            UserName=args.user_name, AccessKeyId=new_key.access_key_id
        )
        return 1

    new_cred = credentials.Credential(
        new_key.access_key_id, new_key.secret_access_key, profile=args.profile
    )

    previous_key = credentials.override_profile(
        args.profile, new_cred, cred_file=args.credential_file
    )

    iam_client.delete_access_key(
        UserName=args.user_name, AccessKeyId=old_key.access_key_id
    )

    if args.verbose:
        print(previous_key, new_cred.aws_access_key_id, sep="->")

    return 0
