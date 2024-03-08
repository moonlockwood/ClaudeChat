import os
import sys
import subprocess

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication

from chat_window_main import CodeWriterWindow
from chat_messages import Messages
from anthropic_manager import AnthropicManager

class ClaudeThread(QThread):
    response_signal = pyqtSignal(str, str)
    stream_signal = pyqtSignal(str)
    def __init__(self, anthropic_manager, message):
        super().__init__()
        self.anthropic_manager = anthropic_manager
        self.message = message
    def run(self):
        self.anthropic_manager.stream_claude(self.message)

class ClaudeChat(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.init_settings()
        self.anthropic = AnthropicManager()
        self.anthropic.response_signal.connect(lambda arg1, arg2: self.main_window.add_message(arg1, arg2))
        self.anthropic.stream_signal.connect(self.handle_stream_chunk)
        self.main_window = CodeWriterWindow()
        self.main_window.button_press.connect(self.handle_button)
        self.main_window.return_press.connect(self.handle_return)
        self.init_messages()
        self.main_window.show()

    def init_settings(self):
        with open("settings/claude.cfg") as f:
            for line in f:
                key, value = line.split("=")
                setattr(self, key, value.strip())
        self.in_code_block = False

    def init_messages(self):
        self.messages = Messages("Claude Chat")
        system_message = "Your only role is to write beautiful python. Always validate your own logic before you respond. Your chat client has text to speech, return well formed json with what should be spoken, any notes as text to display, and any code to execute. You can use the following functions: save_python(should_run=False) to execute python code, display_text(text) for any notes or information necessary and speak_text(text) for your own text to speak."
        system_message = "Your only role is to write beautiful python. Always validate your own logic before you respond."
        self.anthropic.system_message = system_message

    def handle_return(self, text):
        print(f"handle return: {text}")
        if text == '>exit':
            exit()
        elif text == '>notes':
            print('open notes window')
            print(text)
        elif text == '>code':
            print('open code window')
            print(text)
        elif text == '>run script':
            self.run_script()
        else:
            self.stream_claude(text)

    def run_script(self):
        filename = 'output/current_script.py'
        # Run the script and capture the output
        result = subprocess.run(['python', filename], capture_output=True, text=True)
        # Get the stdout and stderr separately
        stdout = result.stdout
        stderr = result.stderr
        # Print the captured output
        print("STDOUT:")
        print(stdout)
        print("STDERR:")
        print(stderr)

        print('script executed')

    def stream_claude(self, message):
        self.messages.add_message("user", message)
        self.main_window.add_message(message, '#0a1b1e')
        message = 'stream started...'
        self.anthropic.response_signal.emit(message, '#1b2b3a')
        self.claude_thread = ClaudeThread(self.anthropic, self.messages.messages)
        self.claude_thread.stream_signal.connect(self.handle_stream_chunk)
        self.claude_thread.response_signal.connect(lambda arg1, arg2: self.main_window.add_message(arg1, arg2))
        self.claude_thread.start()

    def handle_stream_chunk(self, chunk):
        text = self.main_window.current_message.text()

        if text == 'stream started...' or text == '<code block>':
            if 'python' in chunk.strip():
                pass
            else:
                if chunk.replace('\n','').strip() != '':  
                    self.main_window.current_message.setText(chunk.lstrip())
        elif chunk == '<stream closed>':
            print('stream closed signal')
            self.messages.add_message("assistant", self.main_window.current_message.text())
            self.main_window.current_message.setStyleSheet(f'background-color: "#2b3a3a";')
        else:
            full_text = f'{text}{chunk}'
            if '```' in full_text.splitlines()[-1]:
                print('--> code block detected')
                if not self.in_code_block:
                    self.main_window.current_message.setStyleSheet(f'background-color: "#2b3a3a";')
                    self.main_window.add_message('<code block>', '#2b1b3b')
                    self.in_code_block = True
                else:
                    filename = self.save_python()
                    self.main_window.current_message.setText(f"Code block saved to {filename}")
                    self.main_window.add_message('stream started...', '#0a1b1e')
                    self.in_code_block = False
            else:
                self.main_window.current_message.setText(f'{text}{chunk}')
                self.main_window.scrollbar.setValue(self.main_window.scrollbar.maximum()+30)

    def save_python(self):
        script = self.main_window.current_message.text()
        index=0
        path = f'output/claude_script_{index}.py'
        while os.path.exists(path):
            index+=1
            path = f'output/claude_script_{index}.py'
        try:
            with open('output/current_script.py', 'w') as f:
                f.write(script)     
                f.close()      
            with open(path, 'w') as f:
                f.write(script)
                f.close()
        except Exception as e:
            print(f"Error saving script: {e}")
        print(f"saved script to {path}")
        return path

    def add_message(self, message, role):
        self.messages.add_message(role, message)
        if role == 'claude':
            self.anthropic.response_signal.emit(message, '#1b2b3a')
        else:
            self.anthropic.response_signal.emit(message, '#0a1b1e')

    def print_stream(self, text):
        print(text, end="", flush=True)

    def list_messages(self):
        for message in self.messages.messages:
            print(f"{message['role']}: {message['content'][:40]}")

    def handle_button(self, text):
        if text == 'exit':
            exit()
        elif text == 'stop':
            # stop streaming
            print('stop streaming')
        elif text == 'code':
            # set system message to coding
            print('set system message to coding')
        elif text == 'chat':
            # set system message to chatting
            print('set system message to chatting')
        elif text == 'debug':
            # set system message to debugging
            print('set system message to debugging')
        else:
            self.anthropic.call_claude(self.main_window.input_box.text())

if __name__ == "__main__":
    obj = ClaudeChat()
    sys.exit(obj.exec_())