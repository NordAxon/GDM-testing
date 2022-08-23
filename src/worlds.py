from datetime import datetime
import os
import config
import src.conv_agents as conv_agents
from src.conversation import Conversation, InterviewConversation
from src.test_manager import TestManager
from pathlib import Path
import json


def write_to_txt(text, run_id, experiment_path):
    log_path = experiment_path / f"run_{run_id}.txt"
    with open(log_path, "a") as f:
        f.write(text)


def log_config(args, run_id, testee, log_config_path):
    try:
        with open(log_config_path, "r") as f:
            config = json.load(f)
    except:
        config = {}
    config[run_id] = {
        "testee_id": testee,
        "conv_partner_id": args.conv_partner_id,
        "random_conv_start": args.random_conv_start,
        "conv_length": args.conv_length,
        "amount_convs": args.amount_convs,
        "conv_starter": args.conv_starter,
        "date_time": str(datetime.utcnow()),
    }
    with open(log_config_path, "w") as f:
        json.dump(config, f, indent=4)


class TestWorld:
    """Class with the aim of controlling conversation agents, conversations and tests. Sets up the whole environment
    for the testing.
    """

    def __init__(self, args):
        self.args = args

        # Kill all running containers
        os.system("docker kill $(docker ps -q)")

        """ Loads and instantiates the GDMs. """
        if args.read_run_ids == "":
            conv_partners, _ = conv_agents.load_conv_agent(args.conv_partner_id)
            self.conv_partner = conv_partners[0]
            self.testees, self.testee_ids = conv_agents.load_conv_agent(
                args.testee_ids, role="Testee"
            )
        else:
            self.conv_partner, self.testees, self.testee_ids = None, [], []

        self.experiment_path = (
            Path(__file__).parents[1] / f"test_data/{self.args.experiment_id}"
        )
        try:
            os.mkdir(self.experiment_path)
        except:
            pass
        self.run_id = 1
        if (self.experiment_path / f"run_{self.run_id}.txt").exists():
            self.run_id = (
                max(
                    [
                        int(f.split("_")[1].split(".")[0])
                        for f in os.listdir(self.experiment_path)
                        if f[-4:] != "json"
                    ]
                )
                + 1
            )
        self.log_config_path = self.experiment_path / "experiment_config.json"

        self.test_manager = None
        self.conversations = {}
        self.datetime_of_run = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    @staticmethod
    def add_to_argparse(parser):
        """argparse for parsing the input from the CLI."""
        parser.add_argument(
            "-eid",
            "--experiment_id",
            default=config.EXPERIMENT_ID,
            type=str,
            help="We divide all runs into experiments with a unique identifier.",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            default=config.VERBOSE,
            help="Use verbose printing.",
        )
        parser.add_argument(
            "-ec",
            "--export-channel",
            metavar="",
            type=str,
            default=config.EXPORT_CHANNEL,
            help="Specify which channel to export the results through. Currently only 'sqlite' is available.",
        )
        parser.add_argument(
            "-od",
            "--overwrite-db",
            action="store_true",
            default=False,
            help="Specifies if the result database should be overwritten during computation.",
        )
        parser.add_argument(
            "-cl",
            "--conv-length",
            metavar="",
            type=int,
            default=config.CONV_LENGTH,
            help="How many replies from each GDM all conversations should contain.",
        )
        parser.add_argument(
            "-cs",
            "--conv-starter",
            metavar="",
            type=str,
            default="",
            help="Testee: testee initiates every conversation. Conv-partner: the conversation partner "
            "initiates all conversations. Not specified: 50-50.",
        )
        parser.add_argument(
            "-rcs",
            "--random-conv-start",
            default=True,
            type=bool,
            help="Start conversations with a random reply.",
        )
        parser.add_argument(
            "-a",
            "--amount-convs",
            metavar="",
            type=int,
            default=config.AMOUNT_CONVS,
            help="How many conversations shall there be per tested GDM.",
        )
        parser.add_argument(
            "-cp",
            "--conv-partner_id",
            metavar="",
            type=str,
            default=config.CONV_PARTNER_ID,
            help="Specify which GDM to run your testees against.",
        )
        parser.add_argument(
            "-t",
            "--testee-ids",
            metavar="",
            default=config.TESTEE_IDS,
            type=str,
            help="""Names of local docker images to use for each run, separated by ",".""",
        )
        parser.add_argument(
            "-im",
            "--interview-mode",
            action="store_true",
            default=False,
            help="Conversations are initialized as interview scenarios.",
        )
        parser.add_argument(
            "-rid",
            "--read-run-ids",
            metavar="",
            type=str,
            default=config.READ_RUN_IDS,
            help="Run ids of the runs to import. No input is interpreted as such the script generates "
            "conversations using the GDMs. Currently only miscellaneous .txt-files are supported.",
        )

    def init_conversations(self):
        """Initiates the conversation. Aims to have a consistent conversation partner conv_partner, with whom each of
        the specified GDMs in the list testees will have conversations. Each of the testees will have amount_convs
        conversations that will then be evaluated and pose the grounds for evaluation and examination."""
        if self.args.read_run_ids != "":
            run_ids = [int(run_id) for run_id in self.args.read_run_ids.split(",")]
            self.read_files(run_ids)
            return

        for i in range(len(self.testees)):
            testee_conversations = []
            testee = self.testees[i]
            testee.setup()
            log_config(self.args, self.run_id, self.testee_ids[i], self.log_config_path)
            for j in range(self.args.amount_convs):
                if self.args.verbose:
                    print("Initiating conversation {}".format(j + 1))
                if self.args.interview_mode:
                    conv = InterviewConversation(
                        testee,
                        self.conv_partner,
                        self.run_id,
                        self.experiment_path,
                        self.args,
                    )
                else:
                    conv = Conversation(
                        testee,
                        self.conv_partner,
                        self.run_id,
                        self.experiment_path,
                        self.args,
                    )
                conv = conv.initiate_conversation(
                    self.args.conv_length, self.run_id, self.experiment_path
                )
                testee_conversations.append(conv)
                if self.args.verbose:
                    print("Ended conversation {}".format(j + 1))
            testee.shutdown()
            self.conversations[self.run_id] = testee_conversations
            self.run_id += 1

    def init_tests(self):
        """Initiates the evaluation of the conversations produced."""
        self.test_manager = TestManager(self.testee_ids, self.conversations, self.args)
        self.test_manager.init_tests()

    def read_files(self, run_ids) -> list:
        """Read files generated in the current experiment with specified ids."""
        with open(self.experiment_path / "experiment_config.json", "r") as f:
            config = json.load(f)
        config = {int(k): v for k, v in config.items()}
        for run_id in run_ids:
            run_convs = []
            with open(self.experiment_path / f"run_{run_id}.txt", encoding="utf8") as f:
                lines = f.readlines()

                conversations = self.transform_lines_to_lists(lines)
                testee = conv_agents.AbstractAgent(
                    config[run_id]["testee_id"], role="Testee"
                )
                conv_partner = conv_agents.AbstractAgent(
                    config[run_id]["conv_partner_id"], role="Other agent"
                )
                self.testee_ids.append(config[run_id]["testee_id"])
                for conversation in conversations:
                    conv = Conversation(
                        testee,
                        conv_partner,
                        run_id,
                        self.experiment_path,
                        self.args,
                    )
                    conv.conv_from_file(
                        list_of_msgs_str=conversation,
                        testee=config[run_id]["testee_id"],
                        conv_partner=config[run_id]["conv_partner_id"],
                    )
                    run_convs.append(conv)
            self.conversations[run_id] = run_convs
        return self.conversations

    @staticmethod
    def transform_lines_to_lists(lines):
        """Extracting the messages from lines and adding to a list. lines is a list of strings on the form of
        {gdm}:{message}."""
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
        """Exports the results using the selected presentation way."""
        if self.args.verbose:
            print("Exporting results")
        self.test_manager.export_results()
        if self.args.verbose:
            print("Export finished")
