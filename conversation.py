import random

import config


class Conversation:
    """Class for keeping track of a conversation, which includes several messages"""

    def __init__(self):
        self.messages = []

    def initiate_conversation(self, testee, conv_partner, conv_length):
        if random.randint(0, 1) == 0:
            conv_agent1 = testee
            conv_agent2 = conv_partner
        else:
            conv_agent1 = conv_partner
            conv_agent2 = testee

        for i in range(conv_length):
            message = Message(conv_agent1.act(self.messages), conv_agent1.get_id())
            print(conv_agent1.role) if config.VERBOSE else print()
            self.messages.append(message)
            message = Message(conv_agent2.act(self.messages), conv_agent2.get_id())
            print(conv_agent2.role) if config.VERBOSE else print()
            self.messages.append(message)
        return self.messages


class Message:
    """Class for controlling the properties of every message"""

    def __init__(self, message, agent_id):
        self.message = message
        self.agent_id = agent_id

    def belongs_to(self, agent_id):
        return agent_id == self.agent_id

