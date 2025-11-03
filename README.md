# ZR Store Checker Webhook

A small utility that uses the ZombsRoyale.io shop API and posts a formatted Discord webhook
message containing the game's current timed shop (vaulted goods). Each item in the shop is
rendered as a Discord embed. When available, a skin preview image is uploaded to imgbb and
attached as the embed thumbnail.

The project focuses on simple, reliable posting to Discord with clear logging and retry
behavior for robustness.

## Disclaimer

None of the official zombsroyale game assets are used in this project. All the games assets credits go to their respective creators

## Features

- Polls the ZombsRoyale.io public API for the current timed deals and item metadata.
- Builds readable Discord embeds for each timed deal and posts them to a provided webhook URL.
- Optional skin preview thumbnails uploaded to imgbb.
- Robust retry/backoff logic for API failures and webhook posting with error logging.
- Separate logs for errors and successful sends: `logs/errors.log` and `logs/sent.log`.

## Logging

The application writes two log files under `logs/` (created automatically):

- `logs/errors.log` — ERROR-level entries, includes exception stack traces and failed HTTP posts.
- `logs/sent.log` — INFO-level entries for successfully sent messages (timestamp, embed count,
  and the posted message content).

Tip: If you don't want the full message text in `logs/sent.log`, edit `src/webhook.py` to
redact or omit `message` when calling `sent_logger.info(...)`.

## Project structure

```bash
README.md
requirements.txt
src/
  webhook.py           # main script and logic
  assets.py            # asset path helpers
  api_modules/
    zr_api.py          # resilient HTTP wrapper
    imgbb_api.py       # imgbb upload helper
```

## Development notes

- The `create_embeds` function in `src/webhook.py` has been simplified: it now builds an
  ordered list of lines and only includes lines when the corresponding data exists.
- `send_to_discord` returns a boolean indicating overall success and logs failing responses.
- `get_json` in `src/api_modules/zr_api.py` uses simple exponential backoff and basic
  exception handling for transient network issues.

## Troubleshooting

- No message posted to Discord:
  - Verify `WEBHOOK_URL` is set and correct.
  - Check `logs/errors.log` for HTTP status codes or exceptions.
  - If you rely on images, ensure `IMGBB_API_KEY` is set and `assets/game_assets/...` files exist.

- Imgbb upload failures:
  - Check `logs/errors.log` for imgbb API error messages.
  - Validate your `IMGBB_API_KEY` and that your account allows uploads.

## Tests and next steps

- Recommended: add a tiny unit test for `create_embeds` that covers a) full data, and b)
  missing fields.
- Consider adding `RotatingFileHandler` for log rotation to avoid unbounded log growth.
- Optionally add a scheduler (Windows Task Scheduler or CI workflow) to run the script daily.
