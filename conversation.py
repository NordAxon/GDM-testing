import random
from transformers import pipeline, set_seed
import config

""" Sets up a text generator for initiating conversations randomly. """
generator = pipeline('text-generation', model='gpt2')


def generate_random_text(start_str):
    return generator(start_str, max_length=30, num_return_sequences=1)[0]['generated_text']


class Conversation:
    """Class for keeping track of a conversation, which includes several messages"""

    def __init__(self):
        self.messages = []
        self.whos_turn = ""

    """ Function for running one conversation between testee and conv_partner. The function lets every GDM produce 
    conv_length responses with regards to the conversation and last response produced. The messages produced are stored 
    in self.messages which is then returned to TestWorld. """
    def initiate_conversation(self, testee, conv_partner, conv_length):
        self.messages.append(Message(generate_random_text('Hi, '), 'generator', 'generator'))
        print("{}: {}".format('Generated starter', self.messages[0].str()))

        """ Randomizes who will produce the first response (except for the randomized conversation starter). """
        if random.randint(0, 1) == 0:
            self.whos_turn = testee
        else:
            self.whos_turn = conv_partner

        """ Loops 2 * conv_length response requests, where each turn self.whos_turn produces the response and then 
        self.whos_turn is switched to the other conversation partner. """
        for i in range(2 * conv_length):
            message = Message(self.whos_turn.act(self.str_conversation()), self.whos_turn.get_id(),
                              role=self.whos_turn.get_role())
            print("{}: {}".format(self.whos_turn.get_role(), message.str())) if config.VERBOSE else print()
            self.messages.append(message)
            self.switch_turn(testee, conv_partner)
        return self.messages

    """ Function for switching the turn to the agent that did not produce the last response. """
    def switch_turn(self, testee, conv_partner):
        self.whos_turn = testee if self.whos_turn.get_id() == conv_partner.get_id() else conv_partner

    """ Method for converting the list of Messages into a list of strings, so that it is printable. """
    def str_conversation(self):
        stringified_messages = []
        for elem in self.messages:
            stringified_messages.append(elem.str())
        return stringified_messages


class Message:
    """ Class for controlling the properties of every Message"""

    def __init__(self, message, agent_id, role):
        self.message = message
        self.agent_id = agent_id
        self.role = role

    """ Function for checking if a message belongs to the specific agent_id brought as a parameter. """
    def belongs_to(self, agent_id):
        return agent_id == self.agent_id

    """ Stringifies a message. That is, it turns a Message into a printable string. """
    def str(self):
        return self.message

