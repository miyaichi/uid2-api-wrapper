import base64
import boto3
import hashlib
import ipaddress
import json
import logging
import os
import requests
from jinja2 import Environment, FileSystemLoader


def get_secrets():
    """
    Retrieve secrets from AWS Secrets Manager.
    """
    secret_name = os.environ["secret_name"]
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager",
                            region_name=os.environ["AWS_REGION"])
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def check_ip(ip):
    """
    Check if the IP is on the whitelisted.
    """
    if os.environ["ip_white_list"] is not None:
        ip = ipaddress.ip_address(ip)
        networks = [
            ipaddress.ip_network(x.strip())
            for x in str(os.environ["ip_white_list"]).split(",")
        ]
        for network in networks:
            if ip in network:
                return True
        return False
    return True


def normalize_email(email):
    """
    Email Address Normalization.

    1. Remove leading and trailing spaces.
    2. Convert all ASCII characters to lowercase.
    3. In gmail.com email addresses, remove the following characters from the username part of the email address:
      1) The period (. (ASCII code 46)).
         For example, normalize jane.doe@gmail.com to janedoe@gmail.com.
      2) The plus sign (+ (ASCII code 43)) and all subsequent characters.
         For example, normalize janedoe+home@gmail.com to janedoe@gmail.com.
    """
    email = email.strip().lower()
    (user, domain) = email.split("@")
    if domain == "gmail.com":
        user = user.replace(".", "").split("+")[0]
        email = "@".join((user, domain))
    return email


def base64_encoded_sha256(str):
    """
    Base64-encoded SHA256 hashe.
    """
    return base64.b64encode(hashlib.sha256(str.encode()).digest()).decode()


def handler_wrapper(func):
    """
    Decorator to enhance log output of handlers.
    """
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


@handler_wrapper
def uid2_sdk(event, context):
    """
    GET /uid2_sdk

    Get the Client-Side SDK.
    """
    env = Environment(loader=FileSystemLoader("./templates"), trim_blocks=True)
    template = env.get_template("uid2-sdk.tpl.js")
    base_url = "https://{}/{}".format(event["requestContext"]["domainName"],
                                      event["requestContext"]["stage"])
    uid2_url = "{}/{}".format(os.environ["endpoint"], os.environ["version"])

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/javascript;charset=UTF-8"
        },
        "body": template.render({
            "base_url": base_url,
            "uid2_url": uid2_url
        })
    }


@handler_wrapper
def token_generate(event, context):
    """
    GET /token/generate

    Generate a UID2 token from an email address or hashed email address.
    """
    if not check_ip(event["requestContext"]["identity"]["sourceIp"]):
        return {"status": "403", "statusDescription": "Forbidden"}

    secrets = get_secrets()
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
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET"
        },
        "body": response.text
    }
