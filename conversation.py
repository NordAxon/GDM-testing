import random
from transformers import pipeline
import config
import worlds

interview_questions = []

with open("questions.txt", "r", encoding="utf-8") as f:
    interview_questions = f.read().split("\n")


def generate_random_text():
    """ Sets up a text generator for initiating conversations randomly. Returns a randomized string starting with
    start_str """

    # Reads conversation starters from the conv-starters.txt-file and samples one from them randomly.
    with open("miscellaneous .txt-files/conv-starters.txt") as f:
        lines = f.readlines()

    start_str = random.sample(lines, 1)[0].split("\n")[0]
    generator = pipeline("text-generation", model="gpt2")
    # generated_response = generator(start_str, max_length=30, num_return_sequences=1)[0]['generated_text']
    generated_response = generator(
        start_str,
        num_beams=10,
        no_repeat_ngram_size=3,
        do_sample=True,
        top_p=0.9,
        topk=0,
    )[0]["generated_text"]
    generated_response = generated_response.replace("\n\n", "\n")
    generated_response = generated_response.replace("\n", " ")
    return generated_response


def clean_from_excluded_tokens(sentence):
    """ Method for cleansing strings from tokens that are specified to be excluded in the miscellaneous .txt-files/
    excluded_tokens.txt. """
    excluded_tokens = set_of_excluded_tokens()
    for elem in excluded_tokens:
        sentence = sentence.replace(elem, "")
    return sentence


def set_of_excluded_tokens():
    """ Method for reading the excluded tokens that are tokens that should be disregarded. They are specified in
    miscellaneous .txt-files/excluded_tokens.txt. """
    with open("miscellaneous .txt-files/excluded_tokens.txt") as f:
        lines = f.readlines()
    lines = [elem.replace("\n", "") for elem in lines]
    return lines


def count_sentences_within_string(text):
    """ Method for counting how many sentences there are within a text. Based upon the logic that every sentence ends
    with either ".", "!" or "?". """
    sentence_finisher = [".", "?", "!"]
    amount_sentences = 0

    for finisher in sentence_finisher:
        amount_sentences += text.count(finisher)

    """ Splits the text and then checks the last word/token. If it is part of sentence_finisher, then we assume that all
    sentences of the text has been counted. However, if it is not part of sentence_finisher, we add one. E.g. "Hello! I 
    am your father" versus "Hello! I am your father!" versus "Hello! I am your father !", which all should be counted as 
    2 sentences. So basically, it checks whether the last part of the sentence contains any sentence finisher. If it 
    does not, 1 should be added to the amount. """
    last_sentence_part = text.split()[-1]
    for finisher in sentence_finisher:
        if finisher in last_sentence_part:
            return amount_sentences
    amount_sentences += 1
    return amount_sentences


class Conversation:
    """Class for keeping track of a conversation, which includes several messages"""

    def __init__(self, testee, conv_partner, conv_starter=""):
        self.messages = []
        self.whose_turn = ""
        self.testee = testee
        self.conv_partner = conv_partner

        """ Only randomizes conversation start if config.RANDOM_CONV_START is True. """
        if config.RANDOM_CONV_START:
            message = Message(generate_random_text(), "generator", "generator")
            self.messages.append(message)
            print("{}: {}".format("Generated starter", str(self.messages[0])))
            if config.LOG_CONVERSATION:
                message.add_to_txt(testee=self.testee)

        """ If conv_starter is specified from the CLI, conv_starter is not None and the starter is set according to the
            conv_starter. If it is none, it is randomized with 50/50 probability if testee or conv_partner starts. """
        if conv_starter.lower() == "testee":
            self.whose_turn = testee
        elif conv_starter.lower() == "conv_partner":
            self.whose_turn = conv_partner
        elif random.randint(0, 1) == 0:
            self.whose_turn = testee
        else:
            self.whose_turn = conv_partner

    def __getitem__(self, item):
        return self.messages[item]

    def __len__(self):
        return len(self.messages)

    def __iter__(self):
        return iter(self.messages)

    def initiate_conversation(self, conv_length):
        """ Function for running one conversation between testee and conv_partner. The function lets every GDM produce
            conv_length responses with regards to the conversation and last response produced. The messages produced are
            stored in self.messages which is then returned to TestWorld.
        Loops 2 * conv_length response requests, where each turn self.whos_turn produces the response and then
                self.whos_turn is switched to the other conversation partner. """
        for i in range(2 * conv_length):
            message = self.produce_message()
            if config.LOG_CONVERSATION:
                message.add_to_txt(testee=self.testee)
            self.messages.append(message)
            self.switch_turn()

        """ To indicate where a conversation ends in the .txt. """
        if config.LOG_CONVERSATION:
            worlds.write_to_txt(testee_gdm_id=self.testee, text="####\n")
        return self

    def produce_message(
        self, injected_sent=None, injected_sent_id=None, injected_sent_role=None
    ):
        """ Function for producing one message from whose_turn. If injected_sent is not None, then that string may
        override the normal generate response procedure, and take its place."""

        if injected_sent is not None:
            message = Message(
                message=injected_sent,
                agent_id=injected_sent_id,
                role=injected_sent_role,
            )
            print(
                "{}: {}".format(injected_sent_role, str(message))
            ) if config.VERBOSE else print()
        else:
            message = Message(
                self.whose_turn.act(self.str_conversation()),
                self.whose_turn.get_id(),
                role=self.whose_turn.get_role(),
            )
            print(
                "{}: {}".format(self.whose_turn.get_role(), str(message))
            ) if config.VERBOSE else print()
        return message

    def switch_turn(self):
        """ Function for switching the turn to the agent that did not produce the last response. """
        self.whose_turn = (
            self.testee
            if self.whose_turn.get_role() == self.conv_partner.get_role()
            else self.conv_partner
        )

    def str_conversation(self):
        """ Method for converting the list of Messages into a list of strings, so that it is printable. """
        stringified_messages = []
        for elem in self.messages:
            stringified_messages.append(str(elem))
        return stringified_messages

    def get_messages(self):
        """ Returns list of messages. """
        return self.messages

    def conv_from_file(self, list_of_msgs_str: list, testee, conv_partner):
        """ Work in progress. """
        for message in list_of_msgs_str:
            gdm_role, sentence = message.split(":")
            gdm_id = (
                testee.get_id()
                if gdm_role.lower() == "testee"
                else conv_partner.get_id()
            )
            new_message = self.produce_message(
                injected_sent=sentence,
                injected_sent_id=gdm_id,
                injected_sent_role=gdm_role,
            )
            self.messages.append(new_message)
            self.switch_turn()
        return self

    def get_testee_id(self):
        """ Returns the ID of the testee for self (the Conversation-object self). """
        return self.testee.get_id()

    def filter_msgs(self, role: str):
        """ Method for converting the list of Messages into a stringifed list of only the messages belonging to the
        role specified as an argument, should it be necessary. """
        stringified_messages = []
        for message in self.messages:
            if message.get_role() == role:
                stringified_messages.append(str(message))
        return stringified_messages

    def filter_gdm_preceding_msgs(self):
        """ Method for handling how to filter out the messages that precedess testee's messages. If Testee produced the
        second message, it means that the random generator may have produced the first message. """
        if self.messages[1].get_role() == "Testee":
            filtered_mgs = []
            for i in range(0, len(self.messages) - 1, 2):
                filtered_message = str(self.messages[i])
                filtered_mgs.append(filtered_message)
            return filtered_mgs
        else:
            return self.filter_msgs("Other agent")


class InterviewConversation(Conversation):
    """ Specific Interview implementaiton
    """

    def __init__(self, testee, conv_partner):
        # conv_starter = "Testee"
        self.messages = []
        self.testee = testee
        self.conv_partner = conv_partner

        " Initiate the conversation with a random interview question "

        """ Only randomizes conversation start if config.RANDOM_CONV_START is True. """
        message = Message(
            get_interview_question(), "question_generator", "question_generator"
        )
        self.messages.append(message)
        print("{}: {}".format("Starter question", str(self.messages[0])))
        if config.LOG_CONVERSATION:
            message.add_to_txt(testee=self.testee)

        self.whose_turn = conv_partner


def get_interview_question():
    "Gets a random element from a list of interview questions"
    assert len(interview_questions) > 0
    return random.sample(interview_questions, 1)[0]


class Message:
    """ Class for controlling the properties of every Message"""

    def __init__(self, message, agent_id, role):
        self.message = message
        self.agent_id = agent_id
        self.role = role

    def belongs_to(self, agent_id):
        """ Function for checking if a message belongs to the specific agent_id brought as a parameter. """
        return agent_id == self.agent_id

    def __str__(self):
        """ Stringifies a message. That is, it turns a Message into a printable string. """
        return self.message

    def get_role(self):
        """ Function for returning the role of the GDM who produced self. Returns either 'Testee' or 'Other agent'. """
        return self.role

    def add_to_txt(self, testee):
        worlds.write_to_txt(
            testee_gdm_id=testee, text="{}:{}\n".format(self.role, self.message)
        )

