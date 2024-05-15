from __future__ import annotations

import os
import platform
import configparser

from typing import Any

class NitrixConfig():
    
    def __init__(self):
        self.config = configparser.ConfigParser()

        if platform.system() == 'Linux':
            self.default_path = os.path.expanduser('~') + "/.nitrix"
            if os.path.exists(self.default_path):
                self.config.read(self.default_path)
        else:
            raise NotImplementedError("Config not implemented for this OS")
    
    def add_config(self, section: str, key: str, value: Any):
        section_data = self.get_section(section)
        section_data.update({key: value})
        with open(self.default_path, 'w') as fil:
            self.config.write(fil)
            
    def add_configs(self, section: str, data: list[str, Any]):
        section_data = self.get_section(section)
        section_data.update(data)
        with open(self.default_path, 'w') as fil:
            self.config.write(fil)
        
    def get_section(self, section: str):
        if not section in self.config:
            self.config[section] = {}
        return self.config[section]
        
    def get_config(self, section: str, key: str):
        return self.config.get(section, key, fallback=dict())