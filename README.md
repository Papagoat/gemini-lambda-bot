
# A simple Gemini trading bot

This is a simple proof-of-concept Gemini API trading bot. For more info, please [visit my blog post](https://terencelucasyap.com/what-i-learned-from-building-crypto-trading-bot/).

*Use with caution. Code is not optimised.*
## Prerequisites

* Python 3.8
* [Serverless Framework](https://www.serverless.com/)
* AWS Lambda
* AWS SNS
* AWS Secrets Manager
* AWS Elasticache for Redis

## Set up
Follow [this guide](https://terencelucasyap.com/how-to-set-up-vpc/) to set up a VPC for the application.

You will need an IAM role with with the required priviledges to run the above services.

## Deploy

```bash
  $ sls deploy -v
```

  
## Environment Variables

To run this project, you will need the following credentials

| Secret Key  | Description |
|---|---|
| GEMINI_API_KEY | Gemini Account API key for trading access|
| GEMINI_API_SECRET |API Secret |
| REDIS_ENDPOINT | Redis Endpoint for AWS Elasticache |
| TELEGRAM_TOKEN | Token generated by [@BotFather](https://t.me/botfather) |
| TELEGRAM_USER_ID | Chat ID for Telegram notifications |

## What's next?

- Refactor codebase...when I'm not so lazy.
- Implement different strategies. [Read more...](https://www.investopedia.com/articles/active-trading/101014/basics-algorithmic-trading-concepts-and-examples.asp)
- Include backtesting?
- Chilling in my own private island.
## Documentation

* [Gemini REST Api Reference](https://docs.gemini.com/rest-api/)
* [redis-py](https://redis-py.readthedocs.io/en/stable/)
* [Serverless Framework Documentation](https://www.serverless.com/framework/docs/)
  