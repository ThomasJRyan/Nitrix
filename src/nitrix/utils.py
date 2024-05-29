from __future__ import annotations

import os
import pathlib
import hashlib
import platform
import configparser

from typing import Any

class NitrixConfig():
    
    def __init__(self):
        self.config = configparser.ConfigParser()

        if platform.system() == 'Linux':
            self.config_folder = pathlib.Path(os.path.expanduser('~') + "/.nitrix/")
        elif platform.system() == 'Windows':
            self.config_folder = pathlib.Path(os.getenv('LOCALAPPDATA') + "\\Nitrix\\")
        else:
            raise NotImplementedError("Config not implemented for this OS")
        
        os.makedirs(self.config_folder, exist_ok=True)
        if os.path.exists(self.config_folder / 'config'):
            self.config.read(self.config_folder / 'config')
    
    def add_config(self, section: str, key: str, value: Any):
        """Add a configuration key/value to a section

        Args:
            section (str): Section header to add the configuration under
            key (str): Key to associate with the value
            value (Any): Value to store in the configuration
        """
        section_data = self.get_section(section)
        section_data.update({key: value})
        with open(self.config_folder / 'config', 'w') as fil:
            self.config.write(fil)
            
    def add_configs(self, section: str, data: dict[str, Any]):
        """Add multiple configurations to a section at once

        Args:
            section (str): Section header to add the configuration under
            data (dict[str, Any]): A dictionary of configurations to add
        """
        section_data = self.get_section(section)
        section_data.update(data)
        with open(self.config_folder / 'config', 'w') as fil:
            self.config.write(fil)
        
    def get_section(self, section: str):
        if not section in self.config:
            self.config[section] = {}
        return self.config[section]
        
    def get_config(self, section: str, key: str):
        return self.config.get(section, key, fallback=None)
    
    
def clean_room_id(room_id: str):
        if not room_id:
            return room_id
        room_id = room_id.replace("!", "_")
        room_id = room_id.replace(":", "_")
        room_id = room_id.replace(".", "_")
        return room_id
    
def get_user_id_colour(user_id: str):
    MIN, MAX = 1, 6
    hashed = hashlib.md5(user_id.encode()).hexdigest()
    numerical = int(''.join([i for i in hashed if i.isdigit()]))
    return (numerical % MAX) + MIN