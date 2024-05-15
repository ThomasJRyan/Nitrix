import typing

from textual.containers import VerticalScroll, Vertical, Horizontal
from textual.reactive import reactive
from textual.widgets import Label, Static, ContentSwitcher
from textual.css.query import NoMatches

from nio import RoomMessageText, MatrixRoom

class MessageContent(Vertical):
    def __init__(self, message: RoomMessageText, *args, **kwargs):
        sender = Label(message.sender[1:].split(":")[0], classes="sender")
        body = Label(message.body, classes="message-body")
        super().__init__(sender, body, *args, **kwargs)
    

class MessagesContainer(ContentSwitcher):
    messages = dict()
    displayed_messages = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, classes='message-container', **kwargs)
    
    def clean_room_id(self, room_id: str ):
        room_id = room_id.replace("!", "_")
        room_id = room_id.replace(":", "_")
        room_id = room_id.replace(".", "_")
        return room_id
    
    async def update_displayed_messages(self, messages: list):
        """Update messages when displayed_messages is updated

        Args:
            old (list[RoomMessageText]): Old messages
            new (list[RoomMessageText]): New messages
        """
        vert_scroll_id = self.clean_room_id(self.app.current_room)
        try:
            vert_scroll = self.get_child_by_id(vert_scroll_id)
        except NoMatches:
            vert_scroll = VerticalScroll(id=vert_scroll_id)
            self.mount(vert_scroll)
            
        for message in messages:
            if messages not in self.displayed_messages and hasattr(message, "body"):
                vert_scroll.mount(MessageContent(message, classes="message-content"))
                
        self.displayed_messages = messages.copy()
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
        
    async def change_room(self, room_id):
        """Change the messages displayed to the `room_id`s room

        Args:
            room_id (str): Room ID to change to
        """
        messages = self.messages.setdefault(room_id, [])
        if not messages:
            res = await self.app.client.room_messages(room_id, self.app.client.next_batch, limit=25)
            print(res.start)
            print(res.end)
            for msg in res.chunk:
                messages.append(msg)
            messages.reverse()
            
        await self.update_displayed_messages(messages)
        
        vert_scroll_id = self.clean_room_id(self.app.current_room)
        self.current = vert_scroll_id