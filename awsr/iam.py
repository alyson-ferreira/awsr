from typing import Iterable, List
import boto3
import itertools
import time

IAM = boto3.client('iam')


class User:
    __slots__ = (
        "user_name",
        "user_id",
        "arn",
        "path",
        "create_date"
    )

    def __init__(self, **kw):
        self.user_name = kw.get("UserName")
        self.user_id = kw.get("UserId")
        self.arn = kw.get("Arn")
        self.path = kw.get("Path")
        self.create_date = kw.get("CreateDate")


class AccessKey:
    __slots__ = (
        "access_key_id",
        "create_date",
        "secret_access_key",
        "status",
        "user_name",
    )

    def __init__(self, **kw):
        self.access_key_id = kw.get("AccessKeyId")
        self.create_date = kw.get("CreateDate")
        self.secret_access_key = kw.get("SecretAccessKey", "")
        self.status = kw.get("Status")
        self.user_name = kw.get("UserName")


def create_access_key(user: str) -> AccessKey:
    response = IAM.create_access_key(UserName=user)
    return AccessKey(**response["AccessKey"])


def list_users() -> List[User]:
    chunks = map(
        lambda r: r["Users"],
        IAM.get_paginator('list_users').paginate()
    )
    return [User(**user) for chunk in chunks for user in chunk]


def list_access_keys(users: Iterable[str]) -> List[AccessKey]:
    iterchunks = [
        map(lambda r: r['AccessKeyMetadata'],
            IAM.get_paginator('list_access_keys').paginate(UserName=user))
        for user in users
    ]
    chunks = itertools.chain(*iterchunks)
    return [AccessKey(**key) for chunk in chunks for key in chunk]


def list_keys_from_user(user: str) -> List[AccessKey]:
    chunks = map(
        lambda r: r['AccessKeyMetadata'],
        IAM.get_paginator('list_access_keys').paginate(UserName=user)
    )
    return [AccessKey(**key) for chunk in chunks for key in chunk]


def delete_inactive_keys(
    keys: Iterable[AccessKey]
) -> List[AccessKey]:
    keys = filter(lambda k: k.status == "Inactive", keys)
    deleted = []
    for key in keys:
        IAM.delete_access_key(
            UserName=key.user_name,
            AccessKeyId=key.access_key_id
        )
        deleted.append(key)
    return deleted


def delete_access_key(user_name, access_key_id):
    IAM.delete_access_key(
        UserName=user_name,
        AccessKeyId=access_key_id
    )


def get_identity(aws_access_key_id=None, aws_secret_access_key=None):
    sts = boto3.client("sts",
                       aws_access_key_id=aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key)
    return sts.get_caller_identity()


def wait_for_key_avaiability(key: AccessKey, tries=12, interval_seconds=10):
    if key.status == "Inactive":
        raise RuntimeError(f"AWS Key {key.access_key_id} is inactive")

    if not key.secret_access_key:
        raise RuntimeError(f"AWS Key {key.access_key_id} is missing secret")

    for _ in range(10):
        try:
            get_identity(key.access_key_id, key.secret_access_key)
            return True
        except Exception:
            time.sleep(interval_seconds)
            continue
    return False
