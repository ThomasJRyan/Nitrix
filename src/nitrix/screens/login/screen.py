from pathlib import Path

from nio import AsyncClient, RoomMessageText

from textual.screen import Screen
from textual.widgets import Input, Button
from textual.containers import Container, Center

from nitrix.client import client_factory

class LoginError(Exception):
    ...

class LoginForm(Container):
    def compose(self):
        yield Input(id="loginscreen_homeserver", placeholder="Homeserver", value="")
        yield Input(id="loginscreen_username", placeholder="Username", value="")
        yield Input(id="loginscreen_password", placeholder="Password", password=True, value="")
        yield Button(id="loginscreen_submit", label="Login")
        

class LoginScreen(Screen):
    CSS_PATH = Path(__file__).parent / "style.tcss"
    
    def compose(self):
        yield LoginForm()
        
    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "loginscreen_submit":
            await self.try_login()
        
    async def try_login(self):
        homeserver = self.query_one("#loginscreen_homeserver").value
        username = self.query_one("#loginscreen_username").value
        password = self.query_one("#loginscreen_password").value
        
        if (client := await client_factory(homeserver, username, password)):
            client.add_event_callback(self.app.room_message_callback, RoomMessageText)
            self.app.client = client
            self.app.switch_screen("main")
            return

        raise LoginError