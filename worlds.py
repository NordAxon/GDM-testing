import abc
from typing import List, Dict
import config
import conv_agents
from conversation import Conversation


class TestWorld:
    """ Class with the aim of controlling conversation agents, conversations and tests. Sets up the whole environment
    for the testing.
    """

    def __init__(self):
        self.conv_length = 20
        self.amount_convs = 20
        self.report = []
        self.conversations = []
        self.conv_partner = None
        self.testees = None
        self.conv_start = None

    def setup_scripts(self, length_conv_round, amount_convs, tested_gdms, conv_partner, conv_start=None):
        """ Setting up the script based upon the arguments passed from the CLI. """
        self.conv_length = length_conv_round
        self.amount_convs = amount_convs
        self.conv_partner = conv_agents.load_conv_agent(conv_partner)[0]
        self.testees = conv_agents.load_conv_agent(tested_gdms, role='Testee')
        self.conv_start = conv_start

    def init_conversations(self):
        """ Initiates the conversation. Aims to have a consistent conversation partner conv_partner, with whom each of
        the specified GDMs in the list testees will have conversations. Each of the testees will have amount_convs
        conversations that will then be evaluated and pose the grounds for evaluation and examination. """
        conv_partner = self.conv_partner
        for i in range(len(self.testees)):
            testee = self.testees[i]
            conv = Conversation(testee=testee, conv_partner=conv_partner, conv_starter=self.conv_start)
            for j in range(self.amount_convs):
                conv = conv.initiate_conversation(self.conv_length)
                self.conversations.append(conv)
        print(self.conversations)

    def init_tests(self, conversation):
        """ Initiates the evaluation of the conversations produced. """
        print(self.conversations)
        pass
