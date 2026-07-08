# Open-hand Bot

A simple Telegram bot built with Python and Flask to notify you when OpenHands tasks are finished.

## Deployment

This bot is designed to be deployed on Vercel.

### Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather.
- `TELEGRAM_CHAT_ID`: Your Telegram Chat ID where you want to receive notifications.

## Usage

Send a POST request to `/webhook` with the following JSON body:

```json
{
  "message": "OpenHands has finished the task!",
  "chat_id": "YOUR_CHAT_ID" (optional if default is set)
}
```
