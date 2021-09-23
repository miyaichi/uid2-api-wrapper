import boto3
import json
import logging
import os
import requests
import urllib.parse

session = boto3.session.Session()
client = session.client(service_name='secretsmanager',
                        region_name="ap-northeast-1")
response = client.get_secret_value(SecretId=os.environ["secret_name"])
secret = json.loads(response['SecretString'])

AUTHORIZATION_TOKEN = secret['AUTHORIZATION_TOKEN']
ENDPOINT = os.environ["endpoint"]
VERSION = os.environ["version"]


def handler_wrapper(func):
    def decorate(event, context):
        try:
            log = logging.getLogger()
            log.setLevel(logging.DEBUG)
            log.debug("Received event {}".format(json.dumps(event)))
            log.debug("Received body {}".format(
                json.dumps(json.loads(event["body"]))))
        except:
            pass
        response = func(event, context)
        log.debug("Response {}".format(json.dumps(response)))
        return response

    return decorate


def normalize_email(email):
    """
    メールアドレスを正規化する。

    Parameters
    ----------
    email: str
        メールアドレス。

    Returns
    -------
    email : str
        正規化したメールアドレス。
    """
    email = email.strip().lower()
    (user, domain) = email.split("@")
    if domain == "gmail.com":
        user = user.replace(",", "").split("+")[0]
        email = "@".join((user, domain))
    return email


@handler_wrapper
def token_generate(event, context):
    email = email_hash = None
    if event["queryStringParameters"] is not None:
        params = event["queryStringParameters"]
        if "email" in params:
            email = params["email"]
        if "email_hash" in params:
            email_hash = params["email_hash"]

    url = "{}/{}/{}".format(ENDPOINT, VERSION, "token/generate")
    headers = {"Authorization": "Bearer {}".format(AUTHORIZATION_TOKEN)}
    if email:
        params = "email={}".format(normalize_email(email))
    else:
        params = "email_hash={}".format(urllib.parse.quote(email_hash))

    body = status = None
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        if "body" in response.json():
            body = response.json()["body"]
        if "status" in response.json():
            status = response.json()["status"]

    response = {
        "statusCode": response.status_code,
        "body": json.dumps({
            "body": body,
            "status": status
        })
    }

    return response

def token_refresh(event, context):
    refresh_token = None
    if event["queryStringParameters"] is not None:
        params = event["queryStringParameters"]
        if "refresh_token" in params:
            refresh_token = params["refresh_token"]

    url = "{}/{}/{}".format(ENDPOINT, VERSION, "token/refresh")
    headers = {"Authorization": "Bearer {}".format(AUTHORIZATION_TOKEN)}
    params = {"refresh_token": refresh_token}

    body = status = None
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        if "body" in response.json():
            body = response.json()["body"]
        if "status" in response.json():
            status = response.json()["status"]

    response = {
        "statusCode": response.status_code,
        "body": json.dumps({
            "body": body,
            "status": status
        })
    }

    return response

def get_identity_map(event, context):
    email = email_hash = None
    if event["queryStringParameters"] is not None:
        params = event["queryStringParameters"]
        if "email" in params:
            email = params["email"]
        if "email_hash" in params:
            email_hash = params["email_hash"]

    url = "{}/{}/{}".format(ENDPOINT, VERSION, "token/generate")
    headers = {"Authorization": "Bearer {}".format(AUTHORIZATION_TOKEN)}
    if email:
        params = "email={}".format(normalize_email(email))
    else:
        params = "email_hash={}".format(urllib.parse.quote(email_hash))

    body = status = None
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        if "body" in response.json():
            body = response.json()["body"]
        if "status" in response.json():
            status = response.json()["status"]

    response = {
        "statusCode": response.status_code,
        "body": json.dumps({
            "body": body,
            "status": status
        })
    }

    return response