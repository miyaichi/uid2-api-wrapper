# uid2-api-wrapper

Unified ID 2.0 APIをJavascriptから利用するためのWrapper APIを提供します。

Unified ID 2.0 APIは、ベアラートークンを使って認証を行うため、セキュリティ上、サーバーサイドでUID2やUID2 Tokenの生成を行う必要があります。
しかしながら、PoC期間からアプリケーションサーバー側にUnified ID 2.0のサポートを実装することはハードルが高く、PoCの妨げとなる可能性があります。そこで、ベアラートークンではなくIPアドレスで認証を行うWrapper APIをAWS API Gateway + AWS Lambdaで実装しました。ベアラートークンはAWS Security Managerに安全に保存し、IPアドレス制限である程度のセキュリティを担保することができ、API実装をサポートするJavascriptも併せて提供することで、PoCを効率的に実施することができます。

重要: Wrapper APIを利用することで、Unified ID 2.0 APIが本来持つセキュリティレベルとは異なるセキュリティレベルとなるため、テスト環境以外での利用は控えてください。

## Usage

* サポートスクリプトを読み込みます。
```js script
<script type="text/javascript" src="<your base url>/uid2_sdk"></script>
```

* ユーザーがログインしたら、UID2　Tokenを生成し、1st party cookieに保存します。
```js script
__uid2.connect(email);
```

* 現在のUID2 Tokenを取得します。
```js script
advertisingToken = __uid2.getAdvertisingToken();
```

* UID2 Tokenをリフレッシュし、1st party cookieを更新します。
```js script
__uid2.refresh();
```

* ユーザーがログアウトしたら、1st party cookieを削除します。
```js script
__uid2.disconnect();
```

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

* modify config.[stage].json, serverless.yaml
```console
$ vim congig.[stage].json
$ vim serverless.yaml
```

* deploy it
```console
$ serverless deploy [--stage production]
```
