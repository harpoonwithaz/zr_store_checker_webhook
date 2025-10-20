# Discord Automated Webhook Showing ZR's daily store rotation
# Created by: Oliver AKA harpoonwithaz
# Date Created: 2025-09-17

# Module Imports
import requests
import datetime
import os
import time
from dotenv import load_dotenv

# Local imports
from api_modules.imgbb_api import upload_IMG
from api_modules.zr_api import get_json
from assets import get_skin_path

# load url and api key from safe file
load_dotenv()
webhook_url = os.getenv('TESTING_WEBHOOK_URL')
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

def get_item_rarity(data, item_sku):
    if data:
        for skin in data['items']:
            if skin['sku'] == item_sku:
                return skin['rarity']
        else:
            print(f'There was not a skin with the SKU {item_sku} found')
            return None

def create_embed(timed_deals_data, item_info_data) -> list:
    '''Creates a list of formatted embed messages to be sent to discord.
    Parameters:
    - api_data: raw json data from the api
    Returns: List of containing embeds (dicts)'''

    embeds = []
    skin_count = 1
    for skin in timed_deals_data['timedDeals']:
        # Formats for simplicity purposes
        skin_name = skin['name']
        skin_sku = skin['rewards'][0]['itemSku']
        skin_type = skin_sku.split('-')[0].capitalize()
        skin_cost = skin['cost_gems']
        skin_expires = skin['expires']['date'].split(' ') # First item contains date and second item contains time 
        skin_expires_timezone = skin['expires']['timezone']
        
        

        # Obtains skin rarity info from data from api, sets embed color to corresponding rarity
        skin_rarity = get_item_rarity(item_info_data, skin_sku)
        if skin_rarity and skin_rarity in rarity_colors.keys():
            embed_color = rarity_colors[skin_rarity]
        else:
            embed_color = 197379

        # Edit this embed if you want to change the way the message looks
        embed = {
            "description": f"""### Skin #{skin_count}, {skin_name}
            Type: **`{skin_type}`**
            Cost: **`{skin_cost}`** gems
            itemSku: **`{skin_sku}`**
            Rarity: **`{skin_rarity}`**
            Expires: **`{skin_expires[0]}`** at **`{skin_expires[1].split('.')[0]} {skin_expires_timezone}`**""",
            "color": embed_color
            }
        
        # Obtains the asset file and uploads it to imgbb
        skin_asset_path = get_skin_path(skin_sku) # Gets the path to where the skin asset file is located
        
        # Once the asset file is found it uploads it and sets the embed thumbnail to the url
        if skin_asset_path and imgbb_api_key:
            thumbnail_url = upload_IMG(img_location=skin_asset_path, api_key=imgbb_api_key, img_name=skin_sku)
            # Checks if a thumbnail image was passed in, and adds that image as thumbnail in the embed
            if thumbnail_url:
                embed["thumbnail"] = {'url': f'{thumbnail_url}'}
            else:
                embed["description"] = f'{embed["description"]}\n**There is no image preview available for this skin**'
        
        # Checks if it is the first embed and adds the author field
        if skin_count == 1:
            embed["author"] = {
                "name": "Made by: harpoonwithaz",
                "url": "https://github.com/harpoonwithaz",
                "icon_url": "https://github.com/harpoonwithaz.png"
            }

        # Checks if it is the last embed and adds footer field
        if skin_count == len(timed_deals_data['timedDeals']):
            embed["footer"] = {
                "text": "Made using zombsroyale.io API",
                "icon_url": "https://bracketfights.com/images/hero/2019/zombsroyale-afro-tournament-9827/1603079365.png"
            }

        # Adds the counter and appends the embed to the embeds list
        skin_count += 1
        embeds.append(embed)

    # Returns the list of embeds
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
    
    
    # Sends to discord
    if webhook_url:
        requests.post(webhook_url, json = payload)

def main():
    start_time = time.time()
    try:
        timed_deals = get_json(f'{zr_api}timedDeals') # Obtains timed deals data from api
        item_data = get_json(f'{zr_api}items') # Obtains data on every cosmetic from api

        # Creates an a message for discord
        embeds = create_embed(timed_deals, item_data)
        date = datetime.datetime.now()
        message = f'@everyone\n# ZombsRoyale daily vaulted goods\nFor **`{date.strftime('%x')}`** at **`{date.strftime('%X')}`**'

        # Sends the message to the discord webhook
        send_to_discord(msg = message, webhook_username='Daily Store Update', embed_msg = embeds)

        print(f'Message successfully sent to discord webhook: {webhook_url}')
    except Exception as e:
        print(f'There was an error in sending the message: {e}')
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.4f} seconds")

if __name__ == '__main__':
    main()
