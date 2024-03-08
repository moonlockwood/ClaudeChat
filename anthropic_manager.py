import sys
import anthropic
from PyQt5.QtCore import QObject, pyqtSignal

class AnthropicManager(QObject):
    response_signal = pyqtSignal(str, str)
    stream_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_settings()
        self.client = anthropic.Client()
        self.client.api_key=self.api_key
        self.max_tokens = 1024
        self.temperature = 0.82

    def call_claude(self, messages):
        print("- calling claude")
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_message,
                messages=messages
            )
            response = message.content[0].text
            self.add_message(response, 'claude')
        except Exception as e:
            self.handle_exception(e)

    def stream_claude(self, messages):
        print("- opening stream")
        try:
            with self.client.messages.stream(
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=messages,
                model=self.model,
            ) as stream: 
             for text in stream.text_stream:
                self.stream_signal.emit(text)
                self.print_stream(text)
            self.stream_signal.emit('<stream closed>')
            print("\n- stream closed")
        except Exception as e:
            self.stream_signal.emit('<stream closed>')
            print("\n- stream closed due to exception")
            self.handle_exception(e)

    def print_stream(self, text):
        print(text, end="", flush=True)

    def handle_exception(self, e):
        if isinstance(e, anthropic.APIStatusError):
            error_data = e.args[0]
            if isinstance(error_data, dict):
                error_type = error_data.get("error", {}).get("type")
                error_message = error_data.get("error", {}).get("message")
                if error_type == "overloaded_error":
                    print("Error: The API is currently overloaded. Please try again later.")
                else:
                    print(f"API Status Error: {error_type}")
                    print(f"Error Message: {error_message}")
            else:
                print(f"API Status Error: {e}")
        elif isinstance(e, anthropic.APIResponseValidationError):
            print(f"Validation Error: {e}")
        elif isinstance(e, anthropic.AuthenticationError):
            print(f"Authentication Error: {e}")
        elif isinstance(e, anthropic.RateLimitError):
            print(f"Rate Limit Error: {e}")
        else:
            print(f"Unexpected Error: {e}")
    
    def init_settings(self):
        with open("settings/claude.cfg") as f:
            for line in f:
                key, value = line.split("=")
                setattr(self, key, value.strip())