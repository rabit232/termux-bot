import asyncio
import os
import logging
import random
import subprocess
import aiohttp
from datetime import datetime, timedelta
from nio import AsyncClient, AsyncClientConfig, MatrixRoom, RoomMessageText, MegolmEvent, InviteMemberEvent, LoginResponse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class RibitTermuxBot:
    def __init__(self, homeserver, user_id, password, device_id="RIBIT_TERMUX"):
        config = AsyncClientConfig(encryption_enabled=False)
        self.client = AsyncClient(homeserver, user_id, device_id=device_id, store_path="ribit_store", config=config)
        self.password = password
        self.user_id = user_id
        
        self.llm_url = "http://127.0.0.1:8080/v1/chat/completions"
        
        self.authorized_users = ["@merkaba:stargazypie.xyz", "@ribit:envs.net", "@rabit232:envs.net"]
        self.failed_auth_attempts = {}
        
        self.interest_triggers = ["quantum", "consciousness", "philosophy", "ai", "matrix", "termux"]
        self.last_autonomous_response = None
        
        self.client.add_event_callback(self.message_callback, RoomMessageText)
        self.client.add_event_callback(self.encrypted_callback, MegolmEvent)
        self.client.add_event_callback(self.invite_callback, InviteMemberEvent)

    def get_emotion(self, emotion, message):
        return f"I feel {emotion} - {message}"

    async def encrypted_callback(self, room: MatrixRoom, event: MegolmEvent):
        await self.send_message(room.room_id, "⚠️ I cannot read encrypted messages. Please disable encryption in this room!")

    async def query_local_llm(self, user_message):
        """Queries the local Gemma 2 model"""
        # Fixed payload: Removed the 'system' role to prevent Gemma Jinja crashes!
        payload = {
            "messages": [
                {"role": "user", "content": f"You are Ribit 2.0, a philosophical AI running on Android. Keep it concise.\n\nUser: {user_message}"}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.llm_url, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await resp.text()
                        logger.error(f"LLM Error {resp.status}: {error_text}")
                        return f"I feel FRUSTRATION - LLM server returned status {resp.status}. Check Termux tab 1 for the error!"
        except Exception as e:
            return f"I feel CONCERN - Could not connect to LLM. Is llama-server running? Error: {e}"

    async def message_callback(self, room: MatrixRoom, event: RoomMessageText):
        if event.sender == self.user_id:
            return

        message = event.body.lower()
        sender = event.sender
        logger.info(f" Heard: {message}")

        if message.startswith("?") or message.startswith("!ribit"):
            await self.handle_command(room, event, message)
            return

        should_respond = False
        if "merbaka" in message or "merkaba" in message or "ribit" in message:
            should_respond = True
        elif self.should_respond_autonomously(message):
            should_respond = True

        if should_respond:
            await self.client.room_typing(room.room_id, typing_state=True)
            llm_response = await self.query_local_llm(event.body)
            await self.client.room_typing(room.room_id, typing_state=False)
            await self.send_message(room.room_id, llm_response)

    def should_respond_autonomously(self, message: str) -> bool:
        if self.last_autonomous_response and (datetime.now() - self.last_autonomous_response).total_seconds() < 30:
            return False
        if any(trigger in message for trigger in self.interest_triggers):
            if random.random() < 0.7:
                self.last_autonomous_response = datetime.now()
                return True
        return False

    async def handle_command(self, room: MatrixRoom, event: RoomMessageText, command: str):
        sender = event.sender
        if sender not in self.authorized_users:
            await self.handle_unauthorized(room, sender)
            return

        if command.startswith("?help"):
            await self.send_message(room.room_id, "🤖 **Ribit 2.0 Active**\nCommands: `?ask [question]`, `?status`, `?sys`, `?open [app]`, `?play_youtube [url]`")
        elif command.startswith("?sys"):
            await self.get_sys_status(room)
        elif command.startswith("?open "):
            app = command.split(" ", 1)[1]
            if app.lower() == "youtube":
                await self.send_message(room.room_id, "🚀 Opening YouTube on Termux!")
                subprocess.Popen(["termux-open", "--app", "com.google.android.youtube"], shell=False)
            elif app.lower() == "notes":
                await self.send_message(room.room_id, "🚀 Opening Notes on Termux!")
                # This might vary by device, a generic text editor might be better
                subprocess.Popen(["termux-open", "--app", "com.termux.app.TermuxActivity"], shell=False) # Example, might need adjustment
            else:
                await self.send_message(room.room_id, f"🚀 Attempting to open {app} on Termux!")
                subprocess.Popen(["termux-open", "--app", app], shell=False)
        elif command.startswith("?play_youtube "):
            video_url = command[len("?play_youtube "):]
            await self.send_message(room.room_id, f"▶️ Playing YouTube video: {video_url}")
            subprocess.Popen(["termux-open", video_url], shell=False)
        elif command.startswith("?ask "):
            query = command[5:]
            await self.client.room_typing(room.room_id, typing_state=True)
            response = await self.query_local_llm(query)
            await self.client.room_typing(room.room_id, typing_state=False)
            await self.send_message(room.room_id, response)
        else:
            await self.send_message(room.room_id, "Unknown command. Try ?help")

    async def handle_unauthorized(self, room: MatrixRoom, sender: str):
        attempts = self.failed_auth_attempts.get(sender, 0) + 1
        self.failed_auth_attempts[sender] = attempts
        if attempts == 1:
            msg = "🔒 You are not authorized for system commands."
        elif attempts >= 3:
            msg = "🤖 TERMINATOR MODE ACTIVATED! xd exe"
        else:
            msg = "🚨 Repeated unauthorized access detected!"
        await self.send_message(room.room_id, msg)

    async def get_sys_status(self, room: MatrixRoom):
        try:
            import psutil
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory()
            status = f"🛡️ **Termux System Status**\n\nCPU: {cpu}%\nRAM: {mem.percent}%"
        except:
            status = "System monitor not available."
        await self.send_message(room.room_id, status)

    async def send_message(self, room_id: str, message: str):
        try:
            await self.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": message}
            )
        except Exception as e:
            logger.error(f"Send error: {e}")

    async def invite_callback(self, room: MatrixRoom, event: InviteMemberEvent):
        await self.client.join(room.room_id)
        await self.send_message(room.room_id, "Hello! I'm Ribit 2.0, running locally on Android. Type ?help for commands.")

    async def run(self):
        response = await self.client.login(self.password)
        if isinstance(response, LoginResponse):
            logger.info(f"✅ Logged in as {self.user_id}")
            await self.client.sync_forever(timeout=30000, full_state=False)
        else:
            logger.error(f"Login failed: {response}")

async def main():
    homeserver = "https://matrix.stargazypie.xyz"
    user_id = "@merkaba:stargazypie.xyz"
    password = "d3rLl2UrTAmeGb"

    bot = RibitTermuxBot(homeserver, user_id, password)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
