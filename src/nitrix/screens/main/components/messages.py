from __future__ import annotations

import typing
import datetime

from textual.containers import VerticalScroll, Vertical, Horizontal
from textual.reactive import reactive
from textual.widgets import Label, Static, ContentSwitcher
from textual.css.query import NoMatches

from nio import RoomMessageText, MatrixRoom

from nitrix.utils import clean_room_id, get_user_id_colour

class NewMessagesStart():
    ...

class MessageContent(Vertical):
    
    def __init__(self, message: RoomMessageText, *args, **kwargs):
        self.sender_id = message.sender
        self.sender = message.sender[1:].split(":")[0]
        self.messages = []
        super().__init__(*args, **kwargs)
        
        sender_horizonal = Horizontal(classes="sender-container")
        
        # Username
        usercolour = f"username-colour-{get_user_id_colour(self.sender_id)}"
        sender_name = Label(self.sender, classes=f"sender {usercolour}")
        
        # Message sent time
        message_time = message.server_timestamp / 1000
        message_time = datetime.datetime.fromtimestamp(message_time)
        self.message_time = message_time
        message_time = message_time.strftime("%a %d, %I:%M%p")
        sender_time = Label(message_time, classes=f"time")
        
        # Mount the username and message sent time to the horizontal
        sender_horizonal.mount(sender_name)
        sender_horizonal.mount(sender_time)
        
        # Mount the horizontal
        self.mount(sender_horizonal)
        
        # Mount the vertical and add the message
        self.mount(Vertical(id="messages", classes="message-body"))
        self.add_message(message)
        
    def add_message(self, message: RoomMessageText):
        """Adds a message to the container

        Args:
            message (RoomMessageText): The message to add
        """
        if message.sender != self.sender_id:
            return
        self.messages.append(message)
        message_vert = self.query_one("#messages")
        body = getattr(message, "body", None) or "<ERROR: NO MESSAGE BODY>"
        message_vert.mount(Label(body))
        
    @property
    def event_ids(self):
        return [message.event_id for message in self.messages]
    

class MessagesContainer(ContentSwitcher):
    messages = dict()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, classes='message-container', **kwargs)
    
    async def on_mount(self):
        # Once mounted, populate rooms with initial messages
        for room_id in self.app.client.rooms.keys():
            self.run_worker(self.get_initial_messages(room_id))
            
        
    async def get_initial_messages(self, room_id: str):
        """Populate the latest 25 messages for a given room

        Args:
            room_id (str): The room ID to populate the messages for
        """
        # TODO: Turn this into a method of paginating messages
        # TODO: so we can get any number of old messages
        messages = self.messages.setdefault(room_id, [])
        res = await self.app.client.room_messages(room_id, self.app.client.next_batch, limit=25)
        for msg in res.chunk:
            messages.append(msg)
        messages.reverse()
        
    async def remove_new_messages_label(self):
        """Attempt to get the current vertical scroll and remove the new_messages label"""
        vert_scroll = await self.get_room_vert()
        try:
            new_messages = vert_scroll.query_one("#new_messages")
            await new_messages.remove()
        except NoMatches:
            ...
        
    async def get_room_vert(self) -> VerticalScroll | None:
        """Get the current room's vertical scroll

        Returns:
            VerticalScroll: The current room's vertical scroll
        """
        # If not ID, return
        vert_scroll_id = clean_room_id(self.app.current_room)
        if not vert_scroll_id:
            return None
        
        # Try to get an existing VerticalScroll, failing that, create and mount one
        try:
            vert_scroll = self.get_child_by_id(vert_scroll_id)
        except NoMatches:
            vert_scroll = VerticalScroll(id=vert_scroll_id, classes="message-vertical")
            self.mount(vert_scroll)
        return vert_scroll
    
    async def update_displayed_messages(self, messages: list):
        """Update messages when displayed_messages is updated

        Args:
            messages (list[RoomMessageText]): Messages
        """
        # Get the current vertical scroll container
        # If one doesn't exist, return  
        vert_scroll = await self.get_room_vert()
        if not vert_scroll:
            return
            
        # Get a list of event IDs to check against. This
        # is used to ensure we aren't duplicating messages
        event_ids = []
        for child in vert_scroll.children:
            event_ids.extend(getattr(child, "event_ids", []))
            
        for message in messages.copy():
            # The NewMessageStart is used to add the in-line New message notification
            if message is NewMessagesStart:
                # Only add the label if one doesn't already exist
                try:
                    vert_scroll.query_one("#new_messages")
                except NoMatches:
                    vert_scroll.mount(
                        Label("NEW MESSAGES", id="new_messages", classes="new-messages"))
                finally:
                    # We delete it so we're able to add a new one later
                    del messages[messages.index(NewMessagesStart)]
                continue
            
            # Add the message to the vertical scroll container
            elif message.event_id not in event_ids:
                # ! This whole section is so gross... I can do better
                last_message = None
                if vert_scroll.children:
                    for child in vert_scroll.children[::-1]:
                        if not isinstance(child, MessageContent):
                            continue
                        last_message: MessageContent = child
                        break
                    
                message_time = message.server_timestamp / 1000
                message_time = datetime.datetime.fromtimestamp(message_time)
                if last_message and last_message.sender_id == message.sender and (message_time - last_message.message_time).seconds <= 300:
                    last_message.add_message(message)
                else:
                    message_content = MessageContent(message, classes="message-content")
                    vert_scroll.mount(message_content)
                
        # Scroll to the end
        # TODO: Make it so we don't scroll when we're actively looking at a room
        vert_scroll.scroll_end(animate=False)
        
                
    async def add_message(self, room: MatrixRoom, message: RoomMessageText):
        """Adds a message to the messages dict

        Args:
            room (MatrixRoom): Matrix room object
            message (RoomMessageText): Room message text object to add
        """
        # Get the messages for this room
        messages = self.messages.setdefault(room.room_id, [])
        
        # Get the current vertical scroll container
        # If one doesn't exist, return  
        vert_scroll: VerticalScroll = await self.get_room_vert()
        if not vert_scroll:
            return
        
        # Elaborately decide if the New Message notification should be
        # in among the messages
        if not vert_scroll.has_focus and NewMessagesStart not in messages:
            message_box = self.app.query_one("MessageBox")
            if not room.room_id == self.app.current_room or not message_box.has_focus:
                messages.append(NewMessagesStart)
        
        # Add the message to our list of messages
        messages.append(message)
        
        # If we're currently viewing the room in which the message came
        # update the displayed messages
        if room.room_id == self.app.current_room:
            await self.update_displayed_messages(messages)
            return
        
        # Otherwise highlight the radio button corresponding to the room
        room_container = self.app.query_one("RoomsContainer")
        await room_container.highlight_room(room.room_id)
        
    async def change_room(self, room_id: str):
        """Change the messages displayed to the `room_id`s room

        Args:
            room_id (str): Room ID to change to
        """
        # Remove the new messages label in the vertical scroll
        await self.remove_new_messages_label()
        
        # Get the messages from the room and update the displayed messages
        messages = self.messages.setdefault(room_id, [])
        await self.update_displayed_messages(messages)
        
        # Set the current content to the correct vertical scroll
        vert_scroll_id = clean_room_id(self.app.current_room)
        self.current = vert_scroll_id