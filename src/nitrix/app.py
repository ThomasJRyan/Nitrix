from textual.app import App
from textual.widgets import Header, Footer, Placeholder, Tree
from textual.message import Message

from nio import AsyncClient, MatrixRoom, RoomMessageText
from nio.responses import SyncResponse

from nitrix.screens import LoginScreen, MainScreen

class NitrixApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]
    
    SCREENS = {
        "login": LoginScreen(),
        "main": MainScreen(),
    }
    
    def compose(self):
        yield Header()
        yield Footer()
        
    def on_mount(self):
        self.client: AsyncClient = None
        self.current_room = None
        self.push_screen("login")
        
    class ClientUpdate(Message):
        def __init__(self, room: MatrixRoom, message: RoomMessageText):
            self.room = room
            self.message = message
            super().__init__()
        
    def room_message_callback(self, room: MatrixRoom, message: RoomMessageText):
        """Callback for the Matrix client to refer back to

        Args:
            room (MatrixRoom): Matrix room object
            message (RoomMessageText): Room message text object
        """
        self.screen.post_message(self.ClientUpdate(room, message))
        
        
if __name__ == "__main__":
    app = NitrixApp()
    app.run()