import typing

from textual.containers import VerticalScroll, Vertical, Horizontal
from textual.reactive import reactive
from textual.widgets import Label, Static, ContentSwitcher
from textual.css.query import NoMatches

from nio import RoomMessageText, MatrixRoom

from nitrix.utils import clean_room_id

class NewMessagesStart():
    ...

class MessageContent(Vertical):
    def __init__(self, message: RoomMessageText, *args, **kwargs):
        sender = Label(message.sender[1:].split(":")[0], classes="sender")
        body = Label(message.body, classes="message-body")
        super().__init__(sender, body, *args, **kwargs)
    

class MessagesContainer(ContentSwitcher):
    messages = dict()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, classes='message-container', **kwargs)
    
    async def on_mount(self):
        for room_id in self.app.client.rooms.keys():
            self.run_worker(self.get_initial_messages(room_id))
        
    async def get_initial_messages(self, room_id: str):
        messages = self.messages.setdefault(room_id, [])
        res = await self.app.client.room_messages(room_id, self.app.client.next_batch, limit=25)
        for msg in res.chunk:
            messages.append(msg)
        messages.reverse()
    
    async def update_displayed_messages(self, messages: list):
        """Update messages when displayed_messages is updated

        Args:
            messages (list[RoomMessageText]): Messages
        """
        vert_scroll_id = clean_room_id(self.app.current_room)
        try:
            vert_scroll = self.get_child_by_id(vert_scroll_id)
        except NoMatches:
            vert_scroll = VerticalScroll(id=vert_scroll_id)
            self.mount(vert_scroll)
            
        for message in messages:
            event_ids = [child.event_id for child in vert_scroll.children if hasattr(child, "event_id")]
            if message.event_id not in event_ids and hasattr(message, "body"):
                message_content = MessageContent(message, classes="message-content")
                message_content.event_id = message.event_id
                vert_scroll.mount(message_content)
                
        vert_scroll.scroll_end(animate=False)
        
                
    async def add_message(self, room: MatrixRoom, message: RoomMessageText):
        """Adds a message to the messages dict

        Args:
            room (MatrixRoom): Matrix room object
            message (RoomMessageText): Room message text object to add
        """
        messages = self.messages.setdefault(room.room_id, [])
        messages.append(message)
        if room.room_id == self.app.current_room:
            await self.update_displayed_messages(messages)
            return
        
        # messages.append(NewMessagesStart)
        room_container = self.app.query_one("RoomsContainer")
        await room_container.highlight_room(room.room_id)
        
    async def change_room(self, room_id: str):
        """Change the messages displayed to the `room_id`s room

        Args:
            room_id (str): Room ID to change to
        """
        messages = self.messages.setdefault(room_id, [])
        await self.update_displayed_messages(messages)
        vert_scroll_id = clean_room_id(self.app.current_room)
        self.current = vert_scroll_id