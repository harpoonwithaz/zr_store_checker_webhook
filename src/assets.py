import os

def get_skin_path(item_name):
    # Parses the item name to get the type
    item_name_list = item_name.split('-')
    item_type = item_name_list[0]
    target_folder = ''.join((item_name_list[1::])) # Removes the type from the name so its just the skin name itself
    root_path = f'{os.getcwd()}\\assets\\assets\\textures\\skins\\{item_type}'

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

if __name__ == '__main__':
    test_name = 'backpack-daedalus-wings'
    a = get_skin_path(test_name)
    print(a)