import json

from pathlib import Path

from nio import AsyncClient, RoomMessageText

from textual.screen import Screen
from textual.widgets import Input, Button, Checkbox
from textual.containers import Container, Center, Horizontal, Vertical

from nitrix.client import client_factory
from nitrix.utils import NitrixConfig

class LoginError(Exception):
    ...

class LoginForm(Container):
    def compose(self):
        with Vertical(id="input"):
            yield Input(id="loginscreen_homeserver", placeholder="Homeserver", value="")
            yield Input(id="loginscreen_username", placeholder="Username", value="")
            yield Input(id="loginscreen_password", placeholder="Password", password=True, value="")
        with Horizontal(id="submit"):
            yield Checkbox(id="remember_me", label="Remember Me")
            yield Button(id="loginscreen_submit", label="Login")
        

class LoginScreen(Screen):
    CSS_PATH = Path(__file__).parent / "style.tcss"
    
    def compose(self):
        yield LoginForm()
        
    def save_login(self, homeserver, username, password):
        config = NitrixConfig()
        config.add_configs(
            "Credentials",
            {
                "homeserver": homeserver,
                "username": username,
                "password": password,
            }
        )
        
    def get_inputs(self):
        homeserver = self.query_one("#loginscreen_homeserver")
        username = self.query_one("#loginscreen_username")
        password = self.query_one("#loginscreen_password")
        return homeserver, username, password
    
    async def on_mount(self):
        homeserver, username, password = self.get_inputs()
        
        config = NitrixConfig()
        homeserver.value = config.get_config("Credentials", "homeserver") or ""
        username.value = config.get_config("Credentials", "username") or ""
        password.value = config.get_config("Credentials", "password") or ""
        
        if homeserver.value and username.value and password.value:
            await self.try_login()
        
        
    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "loginscreen_submit":
            await self.try_login()
        
    async def try_login(self):
        homeserver, username, password = self.get_inputs()
        
        if (client := await client_factory(homeserver.value, username.value, password.value)):
            client.add_event_callback(self.app.room_message_callback, RoomMessageText)
            self.app.client = client
            
            if self.query_one("#remember_me").value:
                self.save_login(homeserver.value, username.value, password.value)
            
            self.app.switch_screen("main")
            return

        raise LoginError