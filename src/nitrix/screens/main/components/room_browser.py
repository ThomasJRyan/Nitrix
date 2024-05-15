from textual.reactive import reactive
from textual.widgets import Label, RadioButton, RadioSet
from textual.containers import VerticalScroll
from textual.message import Message
  

class RoomsContainer(VerticalScroll):
    rooms = reactive({})
    
    async def watch_rooms(self, old, val):
        room_set = self.query_one(RadioSet)
        room_set.remove_children()
        for room_id, room_obj in val.items():
            btn = RadioButton(room_obj.display_name)
            btn.room_id = room_id
            room_set.mount(btn)
        
    def on_mount(self):
        self.rooms = self.app.client.rooms
        
    def compose(self):
        yield RadioSet()
        
    async def on_radio_set_changed(self, val: RadioSet.Changed):
        self.app.current_room = val.pressed.room_id
        msg_container = self.app.query_one("MessagesContainer")
        self.run_worker(msg_container.change_room(self.app.current_room))