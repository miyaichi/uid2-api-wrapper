# uid2-api-wrapper

## Deploy

* install serverless framework
```console
$ npm install -g serverless
```

* Register Authorization Token in AWS Secrets Manager

  * Secret Name: uid2-secrets
  * Secret Key: AUTHORIZATION_TOKEN
  * Secret Value: <Your Authorization Token>

* cron this repository and install serverless-python-requirements
```console
$ git clone <this repository>
$ cd <this clone directory>
$ npm install --save serverless-python-requirements
```

* deploy it
```console
$ serverless deploy [--stage production]
```
