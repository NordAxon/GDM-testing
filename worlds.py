import abc
from typing import List, Dict
import config
import conv_agents


class TestWorld(abc.ABC):

    def __init__(self):
        """ Object used to keep track of agents, dialogs and tests
        Args:

        """
        self.conv_length = 20
        self.amount_convs = 20
        self.report = []
        self.conversations = []
        self.conv_partner = None
        self.testees = None
        pass

    # Setting up the script based upon the arguments passed from the CLI.
    def setup_scripts(self, length_conv_round, amount_convs, tested_gdms, conv_partner):
        self.conv_length = length_conv_round
        self.amount_convs = amount_convs
        self.conv_partner = conv_agents.load_conv_agent(conv_partner)
        self.testees = conv_agents.load_conv_agent(tested_gdms)

    def init_conversations(self):
        print('Todo')
