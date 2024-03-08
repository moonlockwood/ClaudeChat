class Messages:
    def __init__(self, name):
        self.messages = []
        self.name = name
        print(f"- class init: messages {name}: " + str(self.messages))
       
    def add_message(self, role, content, function_name=None):
        if role == 'function':
            # Ensure function_name is provided for function messages
            if not function_name:
                raise ValueError("Function name is required for function messages")
            # Correctly format the function message
            message = {
                "role": role,
                "name": function_name,
                "content": content,
            }
            print(f"added function message: {message}")
        else:
            message = {"role": role, "content": content}
        self.messages.append(message)

    def delete_last_message(self):
        try:
            print("deleting message: " + str(self.messages.pop()))
        except:
            print("no pop")

    def delete_last_exchange(self):
        try:
            print("deleting message 1: " + str(self.messages.pop()))
        except:
            print("no pop")
        try:
            print("deleting message 2: " + str(self.messages.pop()))
        except:
            print("no pop")
            
    def list_messages(self):
        print()
        print('-'*50)
        for message in self.messages:
            print(f"{message['role']}: {message['content'][:70]}")
        print('-'*71)
      
    def display_messages(self):
        print('-'*50)
        for message in self.messages:
            print(f"{message['role']}: {message['content'][:40]}")
        print('-'*50)
      
    def clear_messages(self):
        self.messages = []
        print(f'messages {self.name} cleared: {str(self.messages)}')

    def get_message(self):
        return self.messages[-1]
    
    def get_message_at(self, index):
        return self.messages[index]
    
    def get_messages(self):
        return self.messages
    
    def save_conversation(self, filename):
        try:
            with open(filename, "w") as file:
                for message in self.messages:
                    file.write(('-'*68)+f"\n{message['role']}:\n{message['content']}\n")
        except:
            print(f'couldnt write file: {filename}')