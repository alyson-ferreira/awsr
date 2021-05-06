"""AWS IAM tools"""

from typing import List
import time

import boto3


class User:
    """AWS IAM User"""

    def __init__(self, **kw):
        self.user_name = kw.get("UserName")
        self.user_id = kw.get("UserId")
        self.arn = kw.get("Arn")
        self.path = kw.get("Path")
        self.create_date = kw.get("CreateDate")


class AccessKey:
    """AWS Access Key"""

    def __init__(self, **kw):
        self.access_key_id = kw.get("AccessKeyId")
        self.create_date = kw.get("CreateDate")
        self.secret_access_key = kw.get("SecretAccessKey")
        self.status = kw.get("Status")
        self.user_name = kw.get("UserName")


def delete_inactive_keys(
    iam, user: str, keys: List[AccessKey]
) -> List[AccessKey]:
    """Remove access keys inactive.

    Args:
        iam: The iam client.
        user: The AWS IAM User name.
        keys: The access keys that belong to the user.

    Returns:
        List containing only active keys.
    """
    for key in keys:
        if key.status == "Inactive":
            iam.delete_access_key(UserName=user, AccessKeyId=key.access_key_id)
    return [key for key in keys if key.status != "Inactive"]


def delete_oldest_key(
    iam, user: str, keys: List[AccessKey]
) -> List[AccessKey]:
    """Remove the oldest access key from the list provided.

    Args:
        iam: The iam client.
        user: The AWS IAM User name.
        keys: The access keys that belong to the user.

    Returns:
        List without the old key sorted by creation date.
    """
    if len(keys) == 1:
        return keys
    sorted_keys = sorted(keys, key=lambda k: k.create_date)
    old_key = next(sorted_keys)
    iam.delete_access_key(UserName=user, AccessKeyId=old_key.access_key_id)
    return list(sorted_keys)


def create_access_key(iam, user: str) -> AccessKey:
    """Creates an access key.

    Args:
        iam: The iam client.
        user: The AWS IAM User name.

    Returns:
        The new access key.
    """
    response = iam.create_access_key(UserName=user)
    return AccessKey(**response["AccessKey"])


def list_keys_from_user(iam, user: str) -> List[AccessKey]:
    """Lists the IAM User access keys.

    Args:
        iam: The iam client.
        user: The AWS IAM User name.

    Returns:
        The new access key.
    """
    result = iam.get_paginator("list_access_keys").paginate(UserName=user)
    chunks = [data["AccessKeyMetadata"] for data in result]
    return [AccessKey(**key) for chunk in chunks for key in chunk]


def get_identity(aws_access_key_id=None, aws_secret_access_key=None):
    """Calls the STS GetCallerIdentity API and returns its result.

    Args:
        aws_access_key_id: The access key to start the session.
        aws_secret_access_key: The secret to start the session.

    Returns:
        The result of GetCallerIdentity call as a dictionary.
    """
    sts = boto3.client(
        "sts",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    return sts.get_caller_identity()


def wait_for_key_avaiability(
    key: AccessKey, tries=12, interval_seconds=10
) -> bool:
    """Checks the access key until it's available or the threshould is reached.

    Args:
        key: The access key to check
        tries: The thresould for failed attempts
        interval_seconds: the period between attempts
    Returns:
        A boolean indicating if the key is working
    Raises:
        RuntimeError in case the key is inactive or if it doesn't have the
        secret
    """

    if key.status == "Inactive":
        raise RuntimeError(f"AWS Key {key.access_key_id} is inactive")

    if not key.secret_access_key:
        raise RuntimeError(f"AWS Key {key.access_key_id} is missing secret")

    for _ in range(tries):
        try:
            get_identity(key.access_key_id, key.secret_access_key)
            return True
        except Exception:
            time.sleep(interval_seconds)
            continue
    return False
