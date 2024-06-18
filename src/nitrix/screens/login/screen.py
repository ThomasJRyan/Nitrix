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

        
    def save_login(self, homeserver: str, username: str, password: str):
        """Saves the login to the config manager

        Args:
            homeserver (str): The homeserver to save
            username (str): The username to save
            password (str): The password to save
        """
        config = NitrixConfig()
        config.add_configs(
            "Credentials",
            {
                "homeserver": homeserver,
                "username": username,
                "password": password,
            }
        )
        
    def get_inputs(self) -> tuple[str, str, str]:
        """Gets the content from the three input boxes

        Returns:
            tuple[str, str, str]: Homeserver, Username, Password
        """
        homeserver = self.query_one("#loginscreen_homeserver")
        username = self.query_one("#loginscreen_username")
        password = self.query_one("#loginscreen_password")
        return homeserver, username, password
    
    async def on_mount(self):

        homeserver, username, password = self.get_inputs()
        
        # Attempt to get the homeserver, username, and password saved
        # in the configuration
        config = NitrixConfig()
        self.app.config = config
        homeserver.value = config.get_config("Credentials", "homeserver") or ""
        username.value = config.get_config("Credentials", "username") or ""
        password.value = config.get_config("Credentials", "password") or ""
        
       

        # If we were able to get the login information, attempt to login
        if homeserver.value and username.value and password.value:
            await self.try_login()
        
        
    async def on_button_pressed(self, event: Button.Pressed):
        # Attempt to login to the server

        from nitrix.screens import PopupScreen #Has to be delayed or you run into circular import

        if event.button.id == "loginscreen_submit":

            try:

                await self.try_login()

            except LoginError as e:
     
                self.app.push_screen(PopupScreen(message="Error: Could not login"))

        
    async def try_login(self):


        """Attempt to login to the Nitrix server

        Raises:
            LoginError: _description_
        """
        homeserver, username, password = self.get_inputs()
        
        # Attempt to create a client
        if (client := await client_factory(homeserver.value, username.value, password.value)):
            # On successful client creation, add an event callback and
            # store the client object in the app
            client.add_event_callback(self.app.room_message_callback, RoomMessageText)
            self.app.client = client
            
            # If the remember me flag was checked, save the login info
            if self.query_one("#remember_me").value:
                self.save_login(homeserver.value, username.value, password.value)
            
            # If we successfully logged in, switch to the main screen
            self.app.switch_screen("main")
            return

        raise LoginError