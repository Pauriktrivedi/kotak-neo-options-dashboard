import logging
import time

class WebSocketHandler:
    def __init__(self, client, manager_callback):
        self.client = client
        self.manager_callback = manager_callback
        self.is_running = False

    def start(self, tokens):
        if not self.client:
            logging.error("No client provided to WebSocketHandler")
            return
            
        self.is_running = True
        try:
            # The SDK handles the actual websocket connection
            # We just provide the tokens and the callback
            self.client.subscribe_quotes(tokens, self.on_message)
        except Exception as e:
            logging.error(f"WebSocket error: {e}")
            self.is_running = False

    def on_message(self, message):
        """
        Processes incoming tick data and routes it to the manager.
        """
        # In a real scenario, this might be a complex JSON
        # message = self.client.parse_message(message)
        if self.manager_callback:
            self.manager_callback(message)

    def stop(self):
        self.is_running = False
        # self.client.unsubscribe_all()
