"""
    Main chat screen of Nitrix. Used for viewing rooms, 
    chat messages, and room members.
"""

import typing

from pathlib import Path

from textual.screen import Screen
from textual.widgets import Input, Button, Label, TextArea
from textual.containers import Container, Center, VerticalScroll, Horizontal, Vertical
from textual.reactive import reactive

from nio import JoinedRoomsResponse, MatrixRoom, RoomMessageText
from nio.responses import Rooms, SyncResponse

from .components import RoomsContainer, MessagesContainer, MessageBox

if typing.TYPE_CHECKING:
    from nitrix.app import NitrixApp
    

class MainScreen(Screen):
    CSS_PATH = Path(__file__).parent / "style.tcss"
    
    def compose(self):
        with Horizontal():
            yield RoomsContainer()
            with Vertical():
                yield MessagesContainer()
                yield MessageBox()
        
    async def on_nitrix_app_client_update(self, client_update: "NitrixApp.ClientUpdate"):
        room = client_update.room
        message = client_update.message
        await self.update_rooms(room, message)
        
    async def update_rooms(self, room: MatrixRoom, message: RoomMessageText):
        msg_container = self.query_one("MessagesContainer")
        self.run_worker(msg_container.add_message(room, message))