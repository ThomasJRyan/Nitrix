from textual.reactive import reactive
from textual.widgets import Label, RadioButton, RadioSet
from textual.containers import VerticalScroll
from textual.message import Message
  
from nitrix.utils import clean_room_id

class RoomsContainer(VerticalScroll):
    rooms = reactive({})
    
    async def watch_rooms(self, old, val):
        room_set = self.query_one(RadioSet)
        room_set.remove_children()
        for room_id, room_obj in val.items():
            cleaned_id = "radio_btn_" + clean_room_id(room_id)
            btn = RadioButton(room_obj.display_name, id=cleaned_id)
            btn.room_id = room_id
            room_set.mount(btn)
        
    def on_mount(self):
        self.rooms = self.app.client.rooms
        
    def compose(self):
        yield RadioSet()
        
    async def on_radio_set_changed(self, val: RadioSet.Changed):
        """Action to perform when a new radio button is selected

        Args:
            val (RadioSet.Changed): The changed radio button event
        """
        self.app.current_room = val.pressed.room_id
        val.pressed.remove_class("room-highlighted")
        msg_container = self.app.query_one("MessagesContainer")
        self.run_worker(msg_container.change_room(self.app.current_room))
        
    async def highlight_room(self, room_id: str):
        """Highlights a room, indicating it has a new message to be viewed

        Args:
            room_id (str): Matrix room ID to be mapped to the radio button
        """
        cleaned_id = "radio_btn_" + clean_room_id(room_id)
        room_set = self.query_one(RadioSet)
        room_set.get_child_by_id(cleaned_id).add_class("room-highlighted")