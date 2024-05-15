from textual import events
from textual.widgets import TextArea, Input

class MessageBox(Input):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, classes='message-box', **kwargs)
    
    async def send_message(self, body):
        await self.app.client.room_send(
            room_id=self.app.current_room,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": body},
        )
    
    async def on_input_submitted(self):
        print(self.app.current_room)
        if not self.app.current_room:
            return
        
        body = self.value
        self.value = ""
        
        self.run_worker(self.send_message(body))
        
        
        