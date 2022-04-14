import os
import aux_functions
import config
import conv_agents
from conversation import Conversation
from test_manager import TestManager


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
        self.test_manager = None
        self.conversations = []
        self.conv_starter = self.args.get('conv_starter')
        config.VERBOSE = self.args.get('verbose')
        config.EXPORT_CHANNEL = self.args.get('export_channel')
        config.GENERATE_DIALOGUE = self.args.get("gen_dialog")

        """ Loads and instantiates the GDMs. """
        self.conv_partner = conv_agents.load_conv_agent(self.args.get('conv_partner'))[0]
        self.testees = conv_agents.load_conv_agent(self.args.get('tested_gdms'), role='Testee')

        """ Makes sure to set up the sqlite-database according to the create-tables.sql-file. """
        if config.EXPORT_CHANNEL == "sqlite":
            print(os.path.exists(aux_functions.db_filename))
            print(config.OVERWRITE_TABLE)
            if not os.path.exists(aux_functions.db_filename) or config.OVERWRITE_TABLE:
                if config.VERBOSE:
                    print("Creates new database file. ")
                os.system("sqlite3 {} < create-tables.sql".format(aux_functions.db_filename))

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
        parser.add_argument('-ec', '--export-channel', metavar='', type=str, default=config.EXPORT_CHANNEL,
                            help="Specify which channel to export the results through. Currently only 'sqlite' "
                                 "is implemented""")
        parser.add_argument('-gd', '--gen-dialog', action="store_true", default=True,
                            help="True: The script generates conversations using the specified GDMs. False: Evaluates a"
                                 " .txt-file")
        parser.add_argument('-v', '--verbose', action="store_true", default=True,
                            help="True: The script prints out what happens so that the user may follow the process. "
                                 "False: A silent run of the script where nothing is printed. Defaults to True.")
        parser.add_argument('-cs', '--conv-starter', metavar='', type=str, default='',
                            help="Testee: testee initiates every conversation. Conv-partner: the conversation partner "
                                 "initiates all conversations. Not specified: 50-50 per conversation who starts that "
                                 "conversation.")
        parser.add_argument('-rf', '--read-file', metavar='', type=str, default='',
                            help="The path to the file you want to read into the script. Interprets the last three"
                                 "letters to interpret what file type it is. No input is interpreted as such the script"
                                 "generates conversations using the GDMs. Currently only miscellaneous .txt-files are"
                                 "supported. ")

    def init_conversations(self):
        """ Initiates the conversation. Aims to have a consistent conversation partner conv_partner, with whom each of
        the specified GDMs in the list testees will have conversations. Each of the testees will have amount_convs
        conversations that will then be evaluated and pose the grounds for evaluation and examination. """
        for i in range(len(self.testees)):
            testee = self.testees[i]
            for j in range(self.amount_convs):
                if config.VERBOSE:
                    print("Initiates conversation {}".format(j + 1))
                conv = Conversation(testee=testee, conv_partner=self.conv_partner, conv_starter=self.conv_starter)
                conv = conv.initiate_conversation(self.conv_length)
                self.conversations.append(conv)
                if config.VERBOSE:
                    print("Ends conversation {}".format(j + 1))

    def init_tests(self):
        """ Initiates the evaluation of the conversations produced. """
        self.test_manager = TestManager(list_testees=self.testees, conversations=self.conversations)
        self.test_manager.init_tests()

    def read_file(self, file_path: str, file_type: str) -> Conversation:
        """ Work in progress to make it possible to read files, as to be able to assess conversations from outside the
        script."""
        conv = Conversation(testee=self.testees[0], conv_partner=self.conv_partner)
        if file_type == ".txt":
            with open(file_path) as f:
                lines = f.readlines()
                conv.conv_from_file(lines=lines)
        return conv

    def export_results(self):
        """ Exports the results using the selected presentation way. """
        if config.VERBOSE:
            print("Exporting results")
        self.test_manager.export_results()
        if config.VERBOSE:
            print("Export finished")
