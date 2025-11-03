import os

version_desktop = 'v4.8.2'
version_mobile = 'v5.8.7'

pack_names = {
    'halloween-2020-chest': 'Pack36',
    'halloween-2023-chest': 'Pack71'
}

def get_skin_path_desktop(item_name):
    ''' 
    For assets unpacked from desktop version of the game.
    Retrieves the file path for a skin asset based on the item name. '''
    
    # Parses the item name
    item_name_list = item_name.split('-')
    item_type = item_name_list[0]
    target_folder = ''.join((item_name_list[1::])) # Removes the type from the name so its just the skin name itself
    root_path = f'{os.getcwd()}\\assets\\game_assets\\desktop_{version_desktop}\\textures\\skins\\{item_type}'

    for root, dirs, files in os.walk(root_path):
        if target_folder in dirs:
            folder_path = os.path.join(root, target_folder)
            files_in_folder = os.listdir(folder_path)

            # Ensure there is at least one file
            if files_in_folder:
                file_path = os.path.join(folder_path, files_in_folder[0])
                return file_path  # Return the first (or only) file found
            else:
                print(f"The folder '{target_folder}' is empty.")
                return None
    return None  # Folder not found

def get_item_path_mobile(item_name):
    '''
    For assets unpacked from mobile version of the game.
    Retrieves the file path for a skin asset based on the item name. '''
    
    # Checks if a packSku was given
    if item_name in pack_names:
        item_name = pack_names[item_name]
    else:
        item_name_list = item_name.split('-')
        item_name = ''.join((item_name_list[1::]))  # Removes the type from the name so its just the skin name itself
    
    root_path = f'{os.getcwd()}\\assets\\game_assets\\mobile_{version_mobile}'
    file_name = f'{item_name}.png'
    full_path = os.path.join(root_path, file_name)

    if os.path.isfile(full_path):
        return full_path
    else:
        return None  # File not found
    

if __name__ == '__main__':
    test_name = 'backpack-daedalus-wings'
    #a = get_skin_path_desktop(test_name)
    a = get_item_path_mobile(test_name)
    print(a)