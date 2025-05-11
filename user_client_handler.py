"""
Module for handling the UserBot client functionality.
This module allows the bot to listen to channels and chats where it's not an admin.
"""

import asyncio
import logging
import os
import threading
import time
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables
client = None
client_thread = None
is_client_running = False
message_queue = asyncio.Queue()
forwarding_function = None

def load_session():
    """Load Telethon session string from environment or generate a new one."""
    session_string = os.environ.get('TELETHON_SESSION_STRING')
    return session_string

def register_bot_forward_function(forward_func):
    """Register the function that will be used to forward messages."""
    global forwarding_function
    forwarding_function = forward_func
    logger.info("Forward function registered")

async def process_message_queue():
    """Process messages in the queue and forward them using the bot."""
    global message_queue, forwarding_function

    logger.info("Message queue processor started")

    while True:
        try:
            # Get a message from the queue
            message = await message_queue.get()

            if forwarding_function:
                # Call the bot's forward function
                forwarding_function(message)

            # Mark the task as done
            message_queue.task_done()

            # Slight delay to prevent flooding
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await asyncio.sleep(1)

async def start_client(session_string, source_entities=None):
    """Start the Telethon client and listen for messages."""
    global client, is_client_running, message_queue

    try:
        # Create the client using session string
        client = TelegramClient(StringSession(session_string), 1234, "dummy")  # Using dummy values

        # Start the client
        await client.start()
        logger.info("Telethon client started successfully")

        # Set is_client_running flag
        is_client_running = True

        # Start the message queue processor
        asyncio.create_task(process_message_queue())

        # Add event handlers for different message types
        @client.on(events.NewMessage(chats=source_entities))
        async def new_message_handler(event):
            """Handle new messages in the source entities."""
            logger.info(f"New message received from {event.chat_id}")

            # Add message to queue for processing
            await message_queue.put(event.message)

        # Keep the client running
        while is_client_running:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Error in Telethon client: {e}")
        is_client_running = False
    finally:
        if client:
            await client.disconnect()
            logger.info("Telethon client disconnected")

def client_thread_function(session_string, source_entities=None):
    """Function to run the client in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(start_client(session_string, source_entities))
    finally:
        loop.close()

def start_user_client(session_string=None, source_entities=None):
    """Start the Telethon client in a separate thread."""
    global client_thread, is_client_running

    if client_thread and client_thread.is_alive():
        logger.warning("Client thread is already running")
        return False

    if not session_string:
        logger.error("Session string is required")
        return False


    # Start the client in a separate thread
    client_thread = threading.Thread(
        target=client_thread_function,
        args=(session_string, source_entities),
        daemon=True
    )
    client_thread.start()

    # Wait a moment to ensure the client started
    time.sleep(2)

    return is_client_running

def stop_user_client():
    """Stop the Telethon client."""
    global is_client_running

    is_client_running = False

    # Wait for thread to finish
    if client_thread:
        client_thread.join(timeout=5)

    return True

def get_client_status():
    """Get the status of the Telethon client."""
    global is_client_running, client_thread

    if client_thread and client_thread.is_alive() and is_client_running:
        return "Running"
    else:
        return "Stopped"