# uid2-api-wrapper

Unified ID 2.0 APIをJavascriptから利用するためのWrapper API。

Unified ID 2.0 APIは、Bearer Tokenを使って認証を行うため、セキュリティ上、サーバーサイドでUID2やUID2 Tokenの生成を行う必要があります。
しかしながら、PoC期間にアプリケーションサーバー側にUnified ID 2.0のサポートを実装することは難しく、PoCの進行を妨げる可能性があります。そこで、Bearer TokenではなくIPアドレスで認証を行うWrapper APIをAWS API Gateway + AWS Lambdaで実装しました。Bearer TokenはAWS Security Managerに安全に保存し、IPアドレス制限である程度のセキュリティを担保することができ、API実装をサポートするJavascriptも併せて提供することで、PoCを効率的に実施することができます。

重要: Wrapper APIを利用することで、Unified ID 2.0 APIが本来持つセキュリティレベルとは異なるセキュリティレベルの運用が必要となることを理解してください。テスト環境での利用を推奨します。

## Usage

* サポートスクリプトを読み込みます。
```js script
<script type="text/javascript" src="[your base url]/uid2_sdk"></script>
```

* ユーザーがログインしたら、ユーザーのメールアドレスからUID2　Tokenを生成し、1st party cookieに保存します。

  <b>Note</b><br>
  connect() 関数に渡されたemailは、SHA256でハッシュしてからUnified ID 2.0 APIに送信しています。

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

## Configuration
設定はconfig.[stage].jsonに記載します。また、AWS Lambdaの環境変数設定で値を変更することができます。

```
{
    "region": "ap-northeast-1",
    "endpoint": "https://integ.uidapi.com",
    "version": "v1",
    "secret_name": "uid2-secrets",
    "ip_white_list": ""
}
```

| Name          | Description                                                      |
| ------------- | ---------------------------------------------------------------- |
| region        | デプロイするAWS Resion                                              |
| endpoint      | Unified ID 2.0のEndpoint                                         |
| version       | Unified ID 2.0のVersion                                          |
| secret_name   | AWS Security Managerに登録したシークレット名                           |
| ip_white_list | アクセスを許可するIPアドレスリスト（カンマ区切り、空白なしで複数記述することができます） |

## Deploy

* Install serverless framework
```console
$ npm install -g serverless
```

* Register Authorization Token in AWS Secrets Manager

  * Secret Name: uid2-secrets
  * Secret Key: AUTHORIZATION_TOKEN
  * Secret Value: [Your Authorization Token]

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

## Credit

- [Unified ID 2.0 Documentation](https://github.com/UnifiedID2/uid2docs)