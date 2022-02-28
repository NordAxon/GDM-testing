import abc
from typing import List, Dict
import config
import conv_agents
from conversation import Conversation


class TestWorld:
    """ Class with the aim of controlling conversation agents, conversations and tests. Sets up the whole environment
    for the testing.
    """

    def __init__(self, args):
        if not config.DEBUG_MODE:
            self.args = vars(args)
        else:
            self.args = args
        self.conv_length = self.args.get('length_conv_round', config.CONV_LENGTH)
        self.amount_convs = self.args.get('amount_convs', config.AMOUNT_CONVS)
        self.report = []
        self.conversations = []
        self.conv_starter = self.args.get('conv_starter')
        config.GENERATE_DIALOGUE = self.args.get("gen_dialog")

        """ Loads and instantiates the GDMs. """
        self.conv_partner = conv_agents.load_conv_agent(self.args.get('conv_partner'))[0]
        self.testees = conv_agents.load_conv_agent(self.args.get('tested_gdms'), role='Testee')

    @staticmethod
    def add_to_argparse(parser):
        """ argparse for parsing the input from the CLI. """
        parser.add_argument('-l', '--length-conv-round', metavar='', type=int, default=config.CONV_LENGTH,
                            help="How many rounds shall there be per "
                                 "conversation until restart")
        parser.add_argument('-a', '--amount-convs', metavar='', type=int, default=config.AMOUNT_CONVS,
                            help="How many conversations shall there be per tested GDM")
        parser.add_argument('-t', '--tested-gdms', metavar='', type=str, default=config.TESTEE,
                            help="Write one or several GDMs you want to test. "
                                 "If several, have them separated by ','. ")
        parser.add_argument('-cp', '--conv-partner', metavar='', type=str, default=config.CONV_PARTNER,
                            help="Specify which GDM to test your GDM against")
        parser.add_argument('-gd', '--gen-dialog', action="store_true", default=True,
                            help="True: The script generates conversations using the specified GDMs. False: Evaluates a"
                                 " .txt-file")
        parser.add_argument('-cs', '--conv-starter', metavar='', type=str, default='',
                            help="Testee: testee initiates every conversation. Conv-partner: the conversation partner "
                                 "initiates all conversations. Not specified: 50-50 per conversation who starts that "
                                 "conversation.")

    def init_conversations(self):
        """ Initiates the conversation. Aims to have a consistent conversation partner conv_partner, with whom each of
        the specified GDMs in the list testees will have conversations. Each of the testees will have amount_convs
        conversations that will then be evaluated and pose the grounds for evaluation and examination. """
        for i in range(len(self.testees)):
            testee = self.testees[i]
            conv = Conversation(testee=testee, conv_partner=self.conv_partner, conv_starter=self.conv_starter)
            for j in range(self.amount_convs):
                conv = conv.initiate_conversation(self.conv_length)
                self.conversations.append(conv)
        print(self.conversations)

    def init_tests(self, conversations):
        """ Initiates the evaluation of the conversations produced. """
        pass

