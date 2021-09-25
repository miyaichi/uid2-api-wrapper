import boto3
import json
import logging
import os
import requests
import urllib.parse
from jinja2 import Environment, FileSystemLoader


def get_secrets(secret_name):
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager",
                            region_name=os.environ["AWS_REGION"])
    response = client.get_secret_value(SecretId=os.environ["secret_name"])
    return json.loads(response["SecretString"])


def normalize_email(email):
    """
    Normalized the email address.

    Parameters
    ----------
    email: str
        email address.

    Returns
    -------
    email : str
        Normalized email address.
    """
    email = email.strip().lower()
    (user, domain) = email.split("@")
    if domain == "gmail.com":
        user = user.replace(".", "").split("+")[0]
        email = "@".join((user, domain))
    return email


def handler_wrapper(func):
    def decorate(event, context):
        if os.environ["ip_white_list"]:
            ip_white_list = [
                x.strip() for x in str(os.environ["ip_white_list"]).split(',')
            ]
            if event["requestContext"]["identity"][
                    "sourceIp"] not in ip_white_list:
                return {'status': '403', 'statusDescription': 'Forbidden'}

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


@handler_wrapper
def uid2_sdk(event, context):
    env = Environment(loader=FileSystemLoader("./templates"), trim_blocks=True)
    template = env.get_template("uid2-sdk.tpl.js")
    base_url = "https://{}/{}".format(event["requestContext"]["domainName"],
                                      event["requestContext"]["stage"])

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/javascript;charset=UTF-8"
        },
        "body": template.render({"base_url": base_url})
    }


@handler_wrapper
def token_generate(event, context):
    secrets = get_secrets(os.environ["secret_name"])
    params = {}
    if event["queryStringParameters"] is not None:
        queryString = event["queryStringParameters"]
        if "email" in queryString:
            params["email"] = normalize_email(queryString["email"])
        if "email_hash" in queryString:
            params["email_hash"] = queryString["email_hash"]

    response = requests.get(
        "{}/{}/{}".format(os.environ["endpoint"], os.environ["version"],
                          "token/generate"),
        headers={
            "Authorization": "Bearer {}".format(secrets["AUTHORIZATION_TOKEN"])
        },
        params="&".join("%s=%s" % (k, v) for k, v in params.items()))

    return {
        "statusCode": response.status_code,
        "headers": {
            "Access-Control-Allow-Headers": 'Content-Type',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET"
        },
        "body": response.text
    }


@handler_wrapper
def token_refresh(event, context):
    secrets = get_secrets(os.environ["secret_name"])
    params = {}
    if event["queryStringParameters"] is not None:
        queryString = event["queryStringParameters"]
        if "refresh_token" in queryString:
            params["refresh_token"] = queryString["refresh_token"]

    response = requests.get(
        "{}/{}/{}".format(os.environ["endpoint"], os.environ["version"],
                          "token/refresh"),
        headers={
            "Authorization": "Bearer {}".format(secrets["AUTHORIZATION_TOKEN"])
        },
        params=params)

    return {
        "statusCode": response.status_code,
        "headers": {
            "Access-Control-Allow-Headers": 'Content-Type',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET"
        },
        "body": response.text
    }


@handler_wrapper
def get_identity_map(event, context):
    secrets = get_secrets(os.environ["secret_name"])
    params = {}
    if event["queryStringParameters"] is not None:
        queryString = event["queryStringParameters"]
        if "email" in queryString:
            params["email"] = normalize_email(queryString["email"])
        if "email_hash" in queryString:
            params["email_hash"] = queryString["email_hash"]

    response = requests.get(
        "{}/{}/{}".format(os.environ["endpoint"], os.environ["version"],
                          "token/generate"),
        headers={
            "Authorization": "Bearer {}".format(secrets["AUTHORIZATION_TOKEN"])
        },
        params="&".join("%s=%s" % (k, v) for k, v in params.items()))

    return {
        "statusCode": response.status_code,
        "headers": {
            "Access-Control-Allow-Headers": 'Content-Type',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET"
        },
        "body": response.text
    }
