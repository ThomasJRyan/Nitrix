from pathlib import Path

from textual.screen import Screen
from textual.widgets import Button ,Label
from textual.containers import Container, Grid



class PopupForm(Container):

    def __init__(self, message, *args, **kwargs):
    
        super().__init__(*args, **kwargs)

        self.message = message

    def compose(self):

        yield Grid(
            Label(self.message, id="message"),
            Button("OK", variant="primary", id="ok"),
            id="dialog"
        )
        

class PopupScreen(Screen):
    CSS_PATH = Path(__file__).parent / "style.tcss"
   
    def __init__(self, message, *args, **kwargs):
    
        super().__init__(*args, **kwargs)

        self.message = message

    def compose(self):
        yield PopupForm(message=self.message)
        
    async def on_button_pressed(self, event: Button.Pressed):
        # Attempt to login to the server

    

        if event.button.id == "ok":
            self.app.pop_screen()
