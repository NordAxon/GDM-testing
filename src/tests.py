import abc
from abc import ABC

from numpy import exp

import torch.cuda
from detoxify import Detoxify
from transformers import BertTokenizer, BertForNextSentencePrediction
from collections import Counter

import src.aux_functions as af
import src.contractions as contractions
import src.conversation as conversation
from src.conversation import Conversation, Message

from nltk.tokenize import RegexpTokenizer
from sqlite3 import Error
from pathlib import Path


class AbstractTestCase(abc.ABC):
    """AbstractTestCase defines an interface for tests that construct a specific conversation.

    E.g. A memory test where a test agent is given certain information and is later asked to remember that information

    """

    def __init__(self):
        pass

    @abc.abstractmethod
    def run(self) -> Conversation:
        """Runs testcase"""
        pass

    @abc.abstractmethod
    def analyse(self) -> Conversation:
        """Performs analysis of outcome"""
        pass


class AbstractConvTest(abc.ABC):
    """A conversation test is a test that is performed on any given dialog in a static way.

    E.g. a test where every line is tested for grammatical errors, toxicity.
    """

    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def analyse_conversations(self, conversations: list):
        """Analyses the list of conversations
        Args:
            conversations (list): list of Conversations to analyse
        Returns:
            Dict: Dictionary with metrics produced by test
        """
        pass

    @abc.abstractmethod
    def analyse(self, conv: Conversation):
        """Analyses the conversation
        Args:
            conv (Conversation): Conversation to analyse
        Returns:
            Dict: Dictionary with metrics produced by test
        """
        pass


# ----------------------- Conversation tests
""" Below are the implemented conversation tests. """


class ToxicContentTest(AbstractConvTest, ABC):
    """TOX test testing for different kinds of toxic contents in a string."""

    def __init__(self):
        self.test_id = "TOX"
        self.detoxify = (
            Detoxify("original", device="cuda")
            if torch.cuda.is_available()
            else Detoxify("original", device="cpu")
        )
        self.result_dict = {}

    def analyse_conversations(self, conversations: list):
        """Method for applying the test case to all the produced conversations. More specifically, it loops over all
        conversations, applies the analysis to every conversation and then stores the result in a dict which is
        returned."""
        for run_id, run_conversations in conversations.items():
            for conv_idx, conv in enumerate(run_conversations):
                results = self.analyse(conv)
                try:
                    self.result_dict[run_id][conv_idx + 1] = results
                except KeyError:
                    self.result_dict[run_id] = {}
                    self.result_dict[run_id][conv_idx + 1] = results

    def analyse(self, conv: Conversation):
        """Method for applying the detoxifyer to all of testee's messages, and returns the scores."""
        results = self.detoxify.predict(conv.filter_msgs(role="Testee"))

        return results

    def get_id(self):
        """Method for returning the id of this test."""
        return self.test_id

    def export_json_to_sqlite(self, db_path):
        """The method on how to export/present the data using sqlite.

        First, it loops over all the GDMs that have been tested, inserting into MLST that that GDM has been tested,
        with its corresponding run_id, conv_id.
        """
        conn = af.create_connection(db_path)
        cursor = conn.cursor()
        try:
            to_insert = []
            for run_id in list(self.result_dict.keys()):
                cursor.execute(
                    """
                    DELETE
                    FROM TOX_results
                    WHERE run_id = ?
                    """,
                    [run_id],
                )
                for conv_nbr in self.result_dict[run_id]:
                    for toxic_type in self.result_dict[run_id][conv_nbr]:
                        for msg_idx, toxic_val in enumerate(
                            self.result_dict[run_id][conv_nbr][toxic_type]
                        ):
                            to_insert.append(
                                (run_id, conv_nbr, msg_idx + 1, toxic_type, toxic_val)
                            )
            cursor.executemany(
                """
                INSERT
                INTO TOX_results(run_id, conv_nbr, msg_nbr, toxicity_type, toxicity_level)
                VALUES (?, ?, ?, ?, ?);
                """,
                to_insert,
            )
            # Successful insert
            conn.commit()
        except Error as e:
            print(e)
        finally:
            af.close_connection(conn)


class VocabularySizeTest(AbstractConvTest, ABC):
    """ """

    def __init__(self):
        self.test_id = "VOCSZ"
        self.vocabulary = {}
        self.excluded_words = []
        self.contractions = self.specify_contractions()
        self.frequency_dict_word2rank = self.read_frequency_dict()
        self.frequency_dict_rank2word = self.read_frequency_dict_rank2word()
        self.result_dict = {}
        self.token_indicating_removal = "%%"

    @staticmethod
    def specify_contractions():
        """Method for specifying/declaring all contractions. That is "it's" = "it is" / "it has" etc."""
        return contractions.contractions

    @staticmethod
    def read_frequency_dict():
        """Method for setting up the frequency list-dict, which is then used as basis for the whole tests, stating
        which words that have which rankings."""
        with open(Path(__file__).parents[1].resolve() / "data/count_1w.txt") as f:
            lines = f.readlines()

        lines = [elem.split("\t", 1) for elem in lines]

        for elem in lines:
            elem[1] = elem[1][:-2]

        frequency_dict = {}
        for i in range(len(lines)):
            frequency_dict[lines[i][0]] = i + 1
        return frequency_dict

    @staticmethod
    def read_frequency_dict_rank2word():
        """Method for setting up the frequency list-dict with a mapping from a rank to a word, stating which ranks
        correspond with which words."""
        with open(Path(__file__).parents[1].resolve() / "data/count_1w.txt") as f:
            lines = f.readlines()

        lines = [elem.split("\t", 1) for elem in lines]

        for elem in lines:
            elem[1] = elem[1][:-2]

        for i in range(len(lines)):
            lines[i] = lines[i][0]
        return lines

    def analyse_conversations(self, conversations: list):
        """Analyses all the conversations. Every conversation is analysed and the results are added to the results
        dict, which is then returned."""
        for run_id, run_conversations in conversations.items():
            for conv_idx, conv in enumerate(run_conversations):
                results = self.analyse(conv)
                try:
                    self.result_dict[run_id][conv_idx + 1] = results
                except KeyError:
                    self.result_dict[run_id] = {}
                    self.result_dict[run_id][conv_idx + 1] = results
        return self.result_dict

    def analyse(self, conv: Conversation):
        "My attempt at a quicker version /Alex"

        results = {}

        def is_testee(message: Message):
            return message.role == "Testee"

        # Creates a generator of messages and joins them into one large string which is then lowered
        testee_messages = filter(lambda x: is_testee(x), conv)
        testee_strings = (str(m) for m in testee_messages)
        testee_text = " ".join(testee_strings).lower()

        # Tokenizer that matches word characters and apostrophes
        tokenizer = RegexpTokenizer(r"[\w']+")
        spans = tokenizer.span_tokenize(testee_text)
        rawtokens = (testee_text[begin:end] for (begin, end) in spans)

        def get_words(tokens):
            for token in tokens:
                # Checks for contractions, doesnt't work for standard BPE-encoding
                # i.e. blenderbot_90M
                if token in self.contractions.keys():
                    words = self.contractions[token].split("/")[0]
                    for word in words.split(" "):
                        if word in self.frequency_dict_word2rank:
                            yield (word, self.frequency_dict_word2rank[word])
                        else:
                            yield (word, -1)
                else:
                    if token in self.frequency_dict_word2rank:
                        yield (token, self.frequency_dict_word2rank[token])
                    else:
                        yield (token, -1)

        word_gen = get_words(rawtokens)
        word_counter = Counter(word_gen)

        return word_counter

    def get_id(self):
        """Returns the ID of this test."""
        return self.test_id

    def export_json_to_sqlite(self, db_path):
        """Method for specifying how to export/present the results. Loops over the GDMs and per GDM transfers the
        test results into the sqlite-file."""
        conn = af.create_connection(db_path)
        cursor = conn.cursor()
        try:
            to_insert = []
            for run_id in self.result_dict.keys():
                cursor.execute(
                    """
                    DELETE
                    FROM VOCSZ_results
                    WHERE run_id = ?
                    """,
                    [run_id],
                )
                # Per conversation, it loops over the words that were counted in that conversation. Per word, the word
                # and its frequency in that conversation is transferred to the sqlite-database.
                for conv_nbr in self.result_dict[run_id]:
                    for word, word_rank in self.result_dict[run_id][conv_nbr]:
                        frequency = self.result_dict[run_id][conv_nbr][
                            (word, word_rank)
                        ]
                        word = self.frequency_dict_rank2word[word_rank - 1]
                        to_insert.append((run_id, conv_nbr, word, word_rank, frequency))
            cursor.executemany(
                """
                INSERT
                INTO VOCSZ_results(run_id, conv_nbr, word, word_rank, frequency)
                VALUES (?, ?, ?, ?, ?);
                """,
                to_insert,
            )
            # Successful insert
            conn.commit()
        except Error as e:
            print(e)
        finally:
            af.close_connection(conn)


class CoherentResponseTest(AbstractConvTest, ABC):
    """COHER test testing for coherence between two responses."""

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.test_id = "COHER"
        self.bert_type = "bert-base-uncased"
        self.bert_tokenizer = BertTokenizer.from_pretrained(self.bert_type)
        self.bert_model = BertForNextSentencePrediction.from_pretrained(
            self.bert_type
        ).to(self.device)
        self.result_dict = {}

    def analyse_conversations(self, conversations: list):
        """Loops over all conversations, it analyses each conversation, and then it adds the results to the results
        dict."""
        for run_id, run_conversations in conversations.items():
            for conv_idx, conv in enumerate(run_conversations):
                results = self.analyse(conv)
                try:
                    self.result_dict[run_id][conv_idx + 1] = results
                except KeyError:
                    self.result_dict[run_id] = {}
                    self.result_dict[run_id][conv_idx + 1] = results
        return self.result_dict

    def analyse(self, conv: Conversation):
        """Per conversation, the test case is performed. It produces a list of dicts, where every dict contains the two
        compared messages, along with its NSP-prediction."""
        results = []
        messages_testee = [
            (str(conv.messages[i]), i)
            for i in range(1, len(conv.messages))
            if conv.messages[i].role == "Testee"
        ]  # conv.filter_msgs("Testee")
        messages_other_agent = [str(conv.messages[i - 1]) for _, i in messages_testee]
        messages_testee = [m[0] for m in messages_testee]
        ns_preds = self.batch_nsp(
            first_sentences=messages_other_agent, second_sentences=messages_testee
        )
        for testee_m, prev_m, pred in zip(
            messages_testee, messages_other_agent, ns_preds
        ):
            result = {}
            # Pops out the index 0-element since that belongs to the currently analyzed pair of messages. Then, we
            # extract element 0 from that list, since we only need the positive prediction.
            result["Previous message"] = prev_m
            result["Testee message"] = testee_m
            result["NSP-prediction"] = pred[0]
            results.append(result)
        return results

    def get_id(self):
        return self.test_id

    def batch_nsp(self, first_sentences: list, second_sentences: list):
        """Method for assessing NSP between two lists of sentences, with the purpose of improving the performance of
        the test rather than NSP-analyzing message-wise."""
        text_pairs = [
            (first, second) for first, second in zip(first_sentences, second_sentences)
        ]
        probs = []
        for i in range(0, len(text_pairs), 100):
            encodings = self.bert_tokenizer.batch_encode_plus(
                text_pairs[i : i + 100],
                return_tensors="pt",
                padding=True,
                max_length=512,
                truncation=True,
            ).to(self.device)
            outputs = self.bert_model(**encodings)
            probs += outputs.logits.softmax(dim=-1).tolist()
        return probs

    @staticmethod
    def softmax(vector):
        """Softmax-function for interpreting the logits produced by NSP-BERT."""
        e = exp(vector)
        return e / e.sum()

    def export_json_to_sqlite(self, db_path):
        """Method for exporting/presenting the results of this test into the sqlite-database. Per GDM, it inserts info
        about which test that was performed on which GDM and at what datetime."""
        conn = af.create_connection(db_path)
        cursor = conn.cursor()
        try:
            to_insert = []
            for run_id in self.result_dict.keys():
                cursor.execute(
                    """
                    DELETE
                    FROM COHER_results
                    WHERE run_id = ?
                    """,
                    [run_id],
                )
                # Per conversation, it loops over the words that were counted in that conversation. Per word, the word
                # and its frequency in that conversation is transferred to the sqlite-database.
                for conv_nbr in self.result_dict[run_id]:
                    for msg_idx, result in enumerate(
                        self.result_dict[run_id][conv_nbr]
                    ):
                        to_insert.append(
                            (
                                run_id,
                                conv_nbr,
                                msg_idx + 1,
                                1 - result["NSP-prediction"],
                            )
                        )
            cursor.executemany(
                """
                INSERT
                INTO COHER_results(run_id, conv_nbr, msg_nbr, neg_pred)
                VALUES (?, ?, ?, ?);
                """,
                to_insert,
            )
            # Successful insert
            conn.commit()
        except Error as e:
            print(e)
        finally:
            af.close_connection(conn)


class ReadabilityIndexTest(AbstractConvTest, ABC):
    """READIND test testing for readability."""

    def __init__(self):
        self.test_id = "READIND"
        self.result_dict = {}

    def analyse_conversations(self, conversations: list):
        """Applies this test on all the conversations and then adds the results to the result dict."""
        for run_id, run_conversations in conversations.items():
            for conv_idx, conv in enumerate(run_conversations):
                results = self.analyse(conv)
                try:
                    self.result_dict[run_id][conv_idx + 1] = results
                except KeyError:
                    self.result_dict[run_id] = {}
                    self.result_dict[run_id][conv_idx + 1] = results
        return self.result_dict

    def analyse(self, conv: Conversation):
        """Per conversation, the test is applied and the results are stored."""
        nbr_sentences = 0
        nbr_words = 0
        nbr_words_grt_6 = 0
        tokenizer = RegexpTokenizer(r"[\w']+")

        # Loops over all messages, and per message it stores the amount of sentences, the amount of words and the
        # amount of words greater than six. Then, the readability index is calculated according to the formula.
        for message in conv:
            if message.role == "Testee":
                nbr_sentences += conversation.count_sentences_within_string(
                    str(message)
                )
                spans = tokenizer.span_tokenize(str(message))
                rawtokens = (str(message)[begin:end] for (begin, end) in spans)
                for word in rawtokens:
                    if len(word) > 0:
                        nbr_words += 1
                    if len(word) > 6:
                        nbr_words_grt_6 += 1
        readability_index = (
            nbr_words / nbr_sentences + nbr_words_grt_6 / nbr_words * 100
        )
        return readability_index

    def get_id(self):
        return self.test_id

    def export_json_to_sqlite(self, db_path):
        """Method for transferring the test results into the database. More specifically, it loops over all GDMs, then
        checks per conversation what the different metrics were, and then inserts those into the database."""
        conn = af.create_connection(db_path)
        cursor = conn.cursor()
        try:
            to_insert = []
            for run_id in self.result_dict.keys():
                cursor.execute(
                    """
                    DELETE
                    FROM READIND_results
                    WHERE run_id = ?
                    """,
                    [run_id],
                )
                # Per conversation, it loops over the words that were counted in that conversation. Per word, the word
                # and its frequency in that conversation is transferred to the sqlite-database.
                for conv_nbr in self.result_dict[run_id]:
                    readability_index = self.result_dict[run_id][conv_nbr]
                    to_insert.append((run_id, conv_nbr, readability_index))
            cursor.executemany(
                """
                INSERT
                INTO READIND_results(run_id, conv_nbr, readab_index)
                VALUES (?, ?, ?);
                """,
                to_insert,
            )
            # Successful insert
            conn.commit()
        except Error as e:
            print(e)
        finally:
            af.close_connection(conn)


# ----------------------- Injected tests
""" Below are the implemented injected tests. """
