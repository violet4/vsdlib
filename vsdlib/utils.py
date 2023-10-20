import os

def create_get_asset_path(caller_file:str):
    assets_folder = os.path.join(os.path.dirname(os.path.abspath(caller_file)), 'assets')
    def get_asset_path(filename:str):
        return os.path.join(assets_folder, filename)
    return get_asset_path
