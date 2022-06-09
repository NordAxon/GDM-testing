import datetime
import os
import aux_functions
import config
import conv_agents
from conversation import Conversation
from test_manager import TestManager


def write_to_txt(testee_gdm_id, text=None):
    with open("{}.txt".format(testee_gdm_id.get_id()), "a") as f:
        f.write(text)


def setup_txt(testee, conv_partner):
    write_to_txt(testee_gdm_id=testee, text="testee:{}\nother agent:{}\n####\n".format(testee.get_id(),
                                                                                       conv_partner.get_id()))


class TestWorld:
    """ Class with the aim of controlling conversation agents, conversations and tests. Sets up the whole environment
    for the testing.
    """

    def __init__(self, args):
        if not config.DEBUG_MODE:
            self.args = vars(args)
            config.VERBOSE = self.args.get('verbose')
            config.INTERNAL_STORAGE_CHANNEL = self.args.get('internal_storage')
            config.EXPORT_CHANNEL = self.args.get('export_channel')
            config.READ_FILE_NAME = self.args.get('read_file_name')
            config.OVERWRITE_TABLE = self.args.get('overwrite_table')
        else:
            self.args = args

        """ Settings that should only be set up as long as the conversations should be generated and not read. """
        if config.READ_FILE_NAME == "":
            self.conv_length = self.args.get('length_conv_round', config.CONV_LENGTH)
            self.amount_convs = self.args.get('amount_convs', config.AMOUNT_CONVS)
            self.conv_starter = self.args.get('conv_starter')

            """ Loads and instantiates the GDMs. """
            self.conv_partner = conv_agents.load_conv_agent(self.args.get('conv_partner'))[0]
            self.testees = conv_agents.load_conv_agent(self.args.get('tested_gdms'), role='Testee')
        else:
            config.RANDOM_CONV_START = False
            config.LOG_CONVERSATION = False

        self.test_manager = None
        self.conversations = []
        self.datetime_of_run = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

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
        parser.add_argument('-is', '--internal-storage', metavar='', type=str, default=config.INTERNAL_STORAGE_CHANNEL,
                            help="Specify which channel to use for the internal storage of results. Currently only "
                                 "'json' is implemented. """)
        parser.add_argument('-v', '--verbose', action="store_true", default=True,
                            help="True: The script prints out what happens so that the user may follow the process. "
                                 "False: A silent run of the script where nothing is printed. Defaults to True.")
        parser.add_argument('-cs', '--conv-starter', metavar='', type=str, default='',
                            help="Testee: testee initiates every conversation. Conv-partner: the conversation partner "
                                 "initiates all conversations. Not specified: 50-50 per conversation who starts that "
                                 "conversation.")
        parser.add_argument('-rf', '--read-file-name', metavar='', type=str, default=config.READ_FILE_NAME,
                            help="The path to the file you want to read into the script. Interprets the letters behind "
                                 "the '.' as the file type. No input is interpreted as such the script generates "
                                 "conversations using the GDMs. Currently only miscellaneous .txt-files are supported.")
        parser.add_argument('-ot', '--overwrite-table', action="store_true", default=False, help="Should the current "
                                 "table be overwritten or should the results be inserted into the currently existing "
                                 "one. True for creating a new table, False for inserting into the currently existing "
                                 "database-file. Defaults to True. ")

    def init_conversations(self):
        """ Initiates the conversation. Aims to have a consistent conversation partner conv_partner, with whom each of
        the specified GDMs in the list testees will have conversations. Each of the testees will have amount_convs
        conversations that will then be evaluated and pose the grounds for evaluation and examination. """
        if config.READ_FILE_NAME != "":
            file_path = config.READ_FILE_NAME
            file_type = file_path.split(".")[1]
            self.read_file(file_path=file_path, file_type=file_type)
            return

        for i in range(len(self.testees)):
            testee = self.testees[i]
            testee.setup()
            if config.LOG_CONVERSATION:
                setup_txt(testee=testee, conv_partner=self.conv_partner)
            for j in range(self.amount_convs):
                if config.VERBOSE:
                    print("Initiates conversation {}".format(j + 1))
                conv = Conversation(testee=testee, conv_partner=self.conv_partner, conv_starter=self.conv_starter)
                conv = conv.initiate_conversation(self.conv_length)
                self.conversations.append(conv)
                if config.VERBOSE:
                    print("Ends conversation {}".format(j + 1))
            testee.shutdown()

    def init_tests(self):
        """ Initiates the evaluation of the conversations produced. """
        self.test_manager = TestManager(list_testees=self.testees, conversations=self.conversations)
        self.test_manager.init_tests()

    def read_file(self, file_path: str, file_type: str) -> list:
        """ Work in progress to make it possible to read files, as to be able to assess conversations from outside the
        script."""
        if file_type == "txt":
            with open(file_path) as f:
                lines = f.readlines()

                testee_str = lines[0].split(":")[1].replace("\n", "")
                conv_partner_str = lines[1].split(":")[1].replace("\n", "")

                """ Adding to the attribute testees, which should be in the form of a list, and the same goes for
                conv_partner. """
                testee = conv_agents.load_conv_agent(testee_str, role="Testee")[0]
                self.testees = [testee]
                conv_partner = conv_agents.load_conv_agent(conv_partner_str, role="Other agent")[0]
                self.conv_partner = conv_partner

                """ Pops all the first elements until the separator '####' is found, due to them being informational 
                details about the conversations, e.g. who is tested and who is the conversation partner. """
                while True:
                    popped_row = lines.pop(0).replace("\n", "")
                    if popped_row == "####":
                        break

                lines = self.transform_lines_to_lists(lines)

                for conversation in lines:
                    conv = Conversation(testee=testee, conv_partner=conv_partner)
                    conv.conv_from_file(list_of_msgs_str=conversation, testee=testee, conv_partner=conv_partner)
                    self.conversations.append(conv)
        return self.conversations

    @staticmethod
    def transform_lines_to_lists(lines):
        """ Extracting the messages from lines and adding to a list. lines is a list of strings on the form of
        {gdm}:{message}. """
        conversations = []
        conversation = []
        for i in range(len(lines)):
            sentence = lines[i].replace("\n", "")
            if sentence == "####":
                conversations.append(conversation)
                conversation = []
            else:
                conversation.append(sentence)
        return conversations

    def export_results(self):
        """ Exports the results using the selected presentation way. """
        if config.VERBOSE:
            print("Exporting results")
        self.test_manager.export_results()
        if config.VERBOSE:
            print("Export finished")