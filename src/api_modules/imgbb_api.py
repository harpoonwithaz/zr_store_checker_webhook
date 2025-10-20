import requests
import base64
import json

def upload_IMG(img_location: str, api_key: str, img_expiry: str = '172800', img_name: str = 'image') -> str | None:
    '''
    Uploads the image to imgbb and returns the link to the image

    Args:
        img_location: Where the img is stored locally
        api_key: api key for imgbb
        img_expiry: time in seconds of how long imgbb will host the image (default 48 hours)
        img_name: name of the image (default 'image')

    Returns:
        str: Link to where the image is hosted 
    '''

    # Credit to Cennef0x
    # I slightly modified his upload img script
    # https://github.com/Cennef0x/imgBB-API/blob/main/screenshoter.py
    
    imgbb_url = 'https://api.imgbb.com/1/upload'

    # Encodes the image in base64
    with open(img_location, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    # Request parameters
    params = (
    ('expiration', img_expiry),# seconds before the image is deleted
    ('key', api_key), #don't change this 
    ('image', encoded_string), # your encoded image
    ('name', img_name) #the image name 
            )
    
    print(f'Sending *POST* request to {imgbb_url}')
    response = requests.post(imgbb_url, data = params) # the request is sent here
    print(f'API Response: "{response}"')
    
    if response.ok: # if code 200 find the link in the response and return it
        json_response = json.loads(response.text) # transform the str into dict
        if "dict" in str(type(json_response)): # check the type of var
            data_response = json_response.get('data') 
            final_url = data_response.get('url') # Gets the URL to the image
            return final_url
        else:
            print(f"ERROR the var is not dict but {type(json_response)}")
            return None
    else:
        print("ERROR {}".format(response.status_code))
        return None
