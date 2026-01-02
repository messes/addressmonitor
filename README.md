# Wallet Watch

**Get Telegram alerts when your Solana wallet receives transactions.**

Deploy in 5 minutes. No code required.

## Deploy to Railway (Easiest)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/xxxxx)

Or manually:

### 1. Get Your API Keys (5 min)

You need 3 things:

| What | Where to get it |
|------|-----------------|
| **Helius API Key** | [helius.dev](https://helius.dev) - Free tier works |
| **Telegram Bot Token** | Message [@BotFather](https://t.me/BotFather) on Telegram, send `/newbot` |
| **Your Telegram Chat ID** | Message [@userinfobot](https://t.me/userinfobot) on Telegram |

### 2. Deploy to Railway

1. Fork this repo
2. Go to [railway.app](https://railway.app) and create a new project
3. Select "Deploy from GitHub repo" and choose your fork
4. Add these environment variables:

```
HELIUS_API_KEY=your_helius_api_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
WATCH_ADDRESS=YourSolanaWalletAddress
WATCH_LABEL=My Wallet
```

5. Deploy! Railway will give you a URL like `https://yourapp.up.railway.app`

### 3. Set Up Helius Webhook

1. Go to [Helius Dashboard](https://dashboard.helius.dev) > Webhooks
2. Create a new webhook:
   - **Webhook URL**: `https://yourapp.up.railway.app/webhook`
   - **Webhook Type**: Enhanced
   - **Account Addresses**: Add your wallet address
   - **Transaction Types**: Any (or select specific types)
3. Copy the **Auth Header** value and add it as `WEBHOOK_SECRET` env var in Railway

### 4. Test It

```bash
curl https://yourapp.up.railway.app/health
# Should return: {"status":"healthy"}
```

You'll now get Telegram notifications for every transaction on your wallet!

---

## Run Locally (Alternative)

```bash
git clone https://github.com/yourusername/wallet-watch.git
cd wallet-watch
cp .env.example .env
# Edit .env with your keys
pip install -e .
wallet-watch start
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HELIUS_API_KEY` | Yes | From [helius.dev](https://helius.dev) |
| `TELEGRAM_BOT_TOKEN` | Yes | From [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Yes | From [@userinfobot](https://t.me/userinfobot) |
| `WATCH_ADDRESS` | Yes | Solana wallet address to monitor |
| `WATCH_LABEL` | No | Label for notifications (default: "My Wallet") |
| `WEBHOOK_SECRET` | No | Helius webhook auth header for security |

## Watch Multiple Wallets

Edit `config.example.yaml` before deploying:

```yaml
watches:
  - address: "Wallet1Address..."
    chain: solana
    label: "Trading Wallet"
    notify: [telegram]

  - address: "Wallet2Address..."
    chain: solana
    label: "Cold Storage"
    notify: [telegram]
```

## Troubleshooting

**Not receiving notifications?**
- Make sure you messaged your bot first (send `/start`)
- Check Railway logs for errors
- Verify your `TELEGRAM_CHAT_ID` is correct

**502 Error?**
- Check that all required env vars are set
- Look at Railway deployment logs

**Webhook not working?**
- Verify the webhook URL in Helius includes `/webhook` at the end
- Check the auth header matches `WEBHOOK_SECRET`

## License

MIT
