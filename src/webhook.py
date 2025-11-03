# Discord Automated Webhook Showing ZR's daily store rotation
# Created by: Oliver AKA harpoonwithaz
# Date Created: 2025-09-17

# Module Imports
import requests
import datetime
import os
import time
import logging
import traceback
from dotenv import load_dotenv

# Local imports
from api_modules.imgbb_api import upload_IMG
from api_modules.zr_api import get_json
from assets import get_item_path_mobile

# load url and api key from env file
load_dotenv()
webhook_url = os.getenv('WEBHOOK_URL')
imgbb_api_key = os.getenv('IMGBB_API_KEY')

# apis
zr_api = 'https://zombsroyale.io/api/shop/available?userKey&sections='

# Rarities and their colors
rarity_colors = {
    'Mythic': 15028046,
    'Legendary': 16549180,
    'Epic': 9264577,
    'Rare': 3653105
}

# Set the application avatar link here
application_avatar = "https://raw.githubusercontent.com/harpoonwithaz/zr_store_checker_webhook/refs/heads/main/assets/webhook_logo.png"

# Console text colors
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
RESET = '\033[0m'


# Initialize file loggers for errors and sent messages
def init_loggers(log_dir=None):
    if log_dir is None:
        log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    error_log_path = os.path.join(log_dir, 'errors.log')
    sent_log_path = os.path.join(log_dir, 'sent.log')

    # Error logger
    error_logger = logging.getLogger('zr_error_logger')
    if not error_logger.handlers:
        error_logger.setLevel(logging.ERROR)
        eh = logging.FileHandler(error_log_path, encoding='utf-8')
        eh.setLevel(logging.ERROR)
        eh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        error_logger.addHandler(eh)

    # Success/sent logger
    sent_logger = logging.getLogger('zr_sent_logger')
    if not sent_logger.handlers:
        sent_logger.setLevel(logging.INFO)
        sh = logging.FileHandler(sent_log_path, encoding='utf-8')
        sh.setLevel(logging.INFO)
        sh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        sent_logger.addHandler(sh)

    return error_logger, sent_logger


# create module-level loggers
error_logger, sent_logger = init_loggers()

def get_item_rarity(data, item_sku):
    if data:
        for skin in data['items']:
            if skin['sku'] == item_sku:
                return skin['rarity']
        else:
            print(f'Could not obtain item rarity: There was not a skin with the SKU {item_sku} found')
            return None

def safe_get(data: dict, possible_keys: list, default=None):
    for key in possible_keys:
        if key in data:
            return data[key]
    return default

def create_embeds(timed_deals_data, item_info_data) -> list:
    """Create a list of Discord embeds from timed deals.

    Simplified approach:
    - Extract necessary fields safely.
    - Build an ordered list of description lines and only include lines when the
      corresponding data exists.
    - Keep thumbnail upload, author (first embed) and footer (last embed).
    """

    embeds = []
    deals = safe_get(timed_deals_data, ['timedDeals'], []) or []
    total = len(deals)

    for idx, timed_deal in enumerate(deals, start=1):
        # Safe extractions
        name = safe_get(timed_deal, ['name'], '**Name Not Found**')

        rewards = safe_get(timed_deal, ['rewards'], []) or []
        sku = None
        if isinstance(rewards, list) and len(rewards) > 0:
            sku = safe_get(rewards[0], ['itemSku', 'packSku'])

        kind = sku.split('-')[0].capitalize() if sku else None

        # cost: prefer gems label if present else coins
        cost = safe_get(timed_deal, ['cost_gems', 'cost_coins'])
        cost_label = 'gems' if 'cost_gems' in timed_deal else ('coins' if 'cost_coins' in timed_deal else '')

        # expires
        expires_date = expires_time = expires_tz = None
        expires_raw = safe_get(timed_deal, ['expires'])
        if expires_raw:
            date_str = safe_get(expires_raw, ['date'])
            if date_str:
                parts = date_str.split(' ')
                if len(parts) >= 2:
                    expires_date = parts[0]
                    expires_time = parts[1].split('.')[0]
                else:
                    expires_date = date_str
            expires_tz = safe_get(expires_raw, ['timezone'])

        # rarity & color
        rarity = get_item_rarity(item_info_data, sku)
        # ensure rarity is a string key before indexing the dict (avoids type-checker issues)
        color = rarity_colors[rarity] if isinstance(rarity, str) and rarity in rarity_colors else 197379

        # Build description lines in the order we want them to appear
        lines = []
        if name:
            lines.append(f'### {name}')
        if kind:
            lines.append(f'Type: **`{kind}`**')
        if cost is not None:
            label = f' {cost_label}' if cost_label else ''
            lines.append(f'Cost: **`{cost}`**{label}')
        if sku:
            lines.append(f'itemSku: **`{sku}`**')
        if rarity:
            lines.append(f'Rarity: **`{rarity}`**')
        if expires_date or expires_time:
            tz = f' {expires_tz}' if expires_tz else ''
            if expires_time:
                lines.append(f'Expires: **`{expires_date}`** at **`{expires_time}{tz}`**')
            else:
                lines.append(f'Expires: **`{expires_date}`**')

        description = "\n".join(lines) if lines else ''

        embed = {
            'description': description,
            'color': color
        }

        # Image thumbnail (if available)
        skin_asset_path = get_item_path_mobile(sku) if sku else None
        if skin_asset_path and imgbb_api_key:
            thumbnail_url = upload_IMG(img_location=skin_asset_path, api_key=imgbb_api_key, img_name=sku or 'skin')
            if thumbnail_url:
                embed['thumbnail'] = {'url': thumbnail_url}
        else:
            # if we couldn't upload, append a short note to the description
            embed['description'] = (embed['description'] + '\n**There is no image preview available for this skin**') if embed['description'] else '**There is no image preview available for this skin**'

        # Add author to first embed
        if idx == 1:
            embed['author'] = {
                'name': 'Made by: harpoonwithaz',
                'url': 'https://github.com/harpoonwithaz',
                'icon_url': 'https://github.com/harpoonwithaz.png'
            }

        # Add footer to last embed
        if idx == total:
            embed['footer'] = {
                'text': 'Made using zombsroyale.io API',
                'icon_url': 'https://bracketfights.com/images/hero/2019/zombsroyale-afro-tournament-9827/1603079365.png'
            }

        embeds.append(embed)

    return embeds

def send_to_discord(msg: str, webhook_username: str = 'Webhook', embed_msg= []):
    # Message payload for discord
    payload = {
        "content" : msg,
        "username" : webhook_username,
        "avatar_url": application_avatar
    }

    # If an embed is passed in
    if embed_msg:
        payload["embeds"] = embed_msg[:10] # slice to avoid >10 error
    
    # Sends to discord. Returns True if all HTTP responses are OK, False otherwise.
    success = True
    responses = []

    if not webhook_url:
        error_logger.error('Webhook URL not set; cannot send message')
        return False

    try:
        # If more than 10 embeds, send in chunks
        if len(embed_msg) > 10:
            for i in range(0, len(embed_msg), 10):
                chunk = embed_msg[i:i + 10]
                chunk_payload = {
                    "content": msg if i == 0 else "",
                    "username": webhook_username,
                    "avatar_url": application_avatar,
                    "embeds": chunk
                }
                resp = requests.post(webhook_url, json=chunk_payload)
                responses.append(resp)
                if not resp.ok:
                    success = False
        else:
            resp = requests.post(webhook_url, json=payload)
            responses.append(resp)
            if not resp.ok:
                success = False
    except Exception as e:
        error_logger.error(f'Exception when sending webhook: {e}\n{traceback.format_exc()}')
        return False

    # Log non-2xx responses
    for r in responses:
        if not r.ok:
            error_logger.error(f'Failed webhook post (status={r.status_code}): {r.text}')

    return success

def main():
    print(CYAN + 'Starting ZR Store Webhook Script' + RESET)
    max_attempts = 3
    backoff_factor = 2
    start_time = time.time()

    for attempt in range(1, max_attempts + 1):
        try:
            print('Fetching API data (attempt %d/%d)' % (attempt, max_attempts))
            timed_deals = get_json(f'{zr_api}timedDeals')  # Obtains timed deals data from api
            if not timed_deals:
                raise RuntimeError('timed_deals API returned no data')

            item_data = get_json(f'{zr_api}items')  # Obtains data on every cosmetic from api
            if not item_data:
                raise RuntimeError('item_data API returned no data')

            print(CYAN + 'Creating embed' + RESET)
            embeds = create_embeds(timed_deals, item_data)
            date = datetime.datetime.now()

            print(CYAN + 'Creating message' + RESET)
            message = f"@everyone\n# Zombsroyale daily vaulted goods\nFor **`{date.strftime('%x')}`** at **`{date.strftime('%X')}`**"

            # Sends the message to the discord webhook
            success = send_to_discord(msg=message, webhook_username='Daily Store Update', embed_msg=embeds)
            if not success:
                raise RuntimeError('Failed to deliver webhook (one or more requests returned non-OK)')

            message += '\n' + str(embeds)

            # Log successful send with useful metadata
            sent_logger.info('Message sent: date=%s embeds=%d message=%s', date.isoformat(), len(embeds), message)
            print(GREEN + f'Message successfully sent to discord webhook: {webhook_url}' + RESET)
            break

        except Exception as e:
            tb = traceback.format_exc()
            error_logger.error('Attempt %d failed: %s\n%s', attempt, e, tb)
            print(YELLOW + f'There was an error in sending the message (attempt {attempt}): {e}. See logs/errors.log for details.' + RESET)

            if attempt == max_attempts:
                print(RED + 'Max attempts reached, aborting.' + RESET)
                break

            # exponential backoff before retrying
            sleep_time = backoff_factor ** attempt
            print(f'Retrying in {sleep_time}s...')
            time.sleep(sleep_time)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.4f} seconds")

if __name__ == '__main__':
    main()
