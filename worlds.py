import abc
from typing import List, Dict
import config
import conv_agents
from conversation import Conversation


class TestWorld(abc.ABC):
    """ Class with the aim of controlling conversation agents, conversations and tests. Sets up the whole environment
    for the testing,
    """

    def __init__(self):
        self.conv_length = 20
        self.amount_convs = 20
        self.report = []
        self.conversations = []
        self.conv_partner = None
        self.testees = None

    """ Setting up the script based upon the arguments passed from the CLI. """
    def setup_scripts(self, length_conv_round, amount_convs, tested_gdms, conv_partner):
        self.conv_length = length_conv_round
        self.amount_convs = amount_convs
        self.conv_partner = conv_agents.load_conv_agent(conv_partner)[0]
        self.testees = conv_agents.load_conv_agent(tested_gdms, role='Testee')

    """ Initiates the conversation. Aims to have a consistent conversation partner conv_partner, with whom each of the 
    specified GDMs in the list testees will have conversation. Each of the testees will have amount_convs conversations
    that will then be evaluated and pose the grounds for evaluation and examination. """
    def init_conversations(self):
        conv_partner = self.conv_partner
        for i in range(len(self.testees)):
            testee = self.testees[i]
            for j in range(self.amount_convs):
                self.conversations.append(Conversation().initiate_conversation(testee, conv_partner, self.conv_length))
        print(self.conversations)
