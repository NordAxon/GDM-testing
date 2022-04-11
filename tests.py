import abc
import datetime
import sqlite3
from abc import ABC

from numpy import exp

import torch.cuda
from detoxify import Detoxify
from transformers import BertTokenizer, BertForNextSentencePrediction
from collections import Counter

import aux_functions
import config
import contractions
import conversation
from conversation import Conversation, Message


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

    @abc.abstractmethod
    def present(self):
        """ Specify how the results should be extracted. E.g. to a .csv-file or to a .sqlite-file. """
        pass


# ----------------------- Conversation tests
""" Below are the implemented conversation tests. """


class ToxicContentTest(AbstractConvTest, ABC):
    """ MLST7 test testing for different kinds of toxic contents in a string."""

    def __init__(self):
        self.test_id = 'MLST7'
        self.detoxify = Detoxify('original', device='cuda') if torch.cuda.is_available() else \
            Detoxify('original', device='cpu')
        self.result_dict = {}

    def analyse_conversations(self, conversations: list):
        for i in range(len(conversations)):
            conv = conversations[i]
            results = self.analyse(conv)

            try:
                self.result_dict[conv.get_testee_id()]['Conversations'][int(i + 1)] = results
            except KeyError:
                self.result_dict[conv.get_testee_id()] = {}
                self.result_dict[conv.get_testee_id()]['Conversations'] = {}
                self.result_dict[conv.get_testee_id()]['Conversations'][int(i + 1)] = results
        return self.result_dict

    def analyse(self, conv: Conversation):
        results = self.detoxify.predict(conv.filter_testee_mgs())
        return results

    def get_id(self):
        return self.test_id

    def present(self):
        if config.PRESENTATION_WAY == "sqlite":
            self.present_through_sqlite()

    def present_through_sqlite(self):
        for gdm_id in list(self.result_dict.keys()):
            date_time = datetime.datetime.now()
            cursor = aux_functions.conn.cursor()
            test_id = "{}:{}:{}".format(gdm_id, self.test_id, date_time)
            try:
                cursor.execute(
                    """
                    INSERT
                    INTO MLST(test_id, gdm_id, date_time_run)
                    VALUES (?, ?, ?);
                    """,
                    [test_id, gdm_id, date_time]
                )
                # Successful insert
                aux_functions.conn.commit()
            except sqlite3.Error as er:
                # Failed insert.
                print("Error occurred while inserting into MLST-table. Error was {}.".format(er))
            for conv_nbr in self.result_dict[gdm_id]['Conversations']:
                for toxic_type in self.result_dict[gdm_id]['Conversations'][conv_nbr]:
                    for toxic_val in self.result_dict[gdm_id]['Conversations'][conv_nbr][toxic_type]:
                        cursor = aux_functions.conn.cursor()
                        try:
                            cursor.execute(
                                """
                                INSERT
                                INTO MLST7_results(test_id, conv_nbr, toxicity_type, toxicity_level)
                                VALUES (?, ?, ?, ?);
                                """,
                                [test_id, conv_nbr, toxic_type, toxic_val]
                            )
                            # Successful insert
                            aux_functions.conn.commit()
                        except sqlite3.Error as er:
                            # Failed insert.
                            print(er)


class VocabularySizeTest(AbstractConvTest, ABC):
    """ """

    def __init__(self):
        self.test_id = 'MLST2'
        self.vocabulary = {}
        self.excluded_words = []
        self.excluded_tokens = conversation.set_of_excluded_tokens()
        self.contractions = self.specify_contractions()
        self.frequency_dict = self.read_frequency_dict()
        self.result_dict = {}

    @staticmethod
    def specify_contractions():
        return contractions.contractions

    @staticmethod
    def read_frequency_dict():
        with open('miscellaneous .txt-files/count_1w.txt') as f:
            lines = f.readlines()

        lines = [elem.split('\t', 1) for elem in lines]

        for elem in lines:
            elem[1] = elem[1][:-2]

        frequency_dict = {}
        for i in range(len(lines)):
            frequency_dict[lines[i][0]] = {
                'rank': i + 1
            }
        return frequency_dict

    def analyse_conversations(self, conversations: list):
        for i in range(len(conversations)):
            conv = conversations[i]
            results = self.analyse(conv)

            try:
                self.result_dict[conv.get_testee_id()]['Conversations'][int(i + 1)] = results
            except KeyError:
                self.result_dict[conv.get_testee_id()] = {}
                self.result_dict[conv.get_testee_id()]['Conversations'] = {}
                self.result_dict[conv.get_testee_id()]['Conversations'][int(i + 1)] = results
        return self.result_dict

    def analyse(self, conv: Conversation):
        """ Function for storing words used by the GDM to keep track of its vocabulary.

        Loops over all messages and per message, it splits it in order to isolate the words used. Then it removed
        tokens such as ',', '.', '?', '!'. After these processes, it is added to the dict, either adds 1 to the amount
        of usages for that word, or sets it to one if it is a new word. """
        testee_id = conv.get_testee_id()
        if testee_id not in self.vocabulary:
            self.vocabulary[testee_id] = {
                'word_counter': Counter(),
                'frequency_word_list': {},
                'non_frequent_words': {}
            }

        for elem in conv:
            if elem.get_role() != "Testee":
                continue
            word_array = str(elem).split()

            for word in word_array:
                """ Removes tokens defined in the constructor from strings, and if the word is defined in the
                constructor as an "excluded" word, it is not counted. """
                word = word.lower()
                word = conversation.clean_from_excluded_tokens(word)
                if word in self.excluded_words:
                    continue
                if word in self.contractions:
                    word = self.find_contraction(word)
                else:
                    word = [word]
                counter = Counter(word)
                self.vocabulary[testee_id]['word_counter'] = self.vocabulary[testee_id]['word_counter'] + counter
                for word_elem in word:
                    try:
                        self.vocabulary[testee_id]['frequency_word_list'][self.frequency_dict[word_elem]['rank']] = \
                            self.vocabulary[testee_id]['word_counter'][word_elem]
                    except KeyError:
                        if word_elem in self.vocabulary[testee_id]['non_frequent_words']:
                            self.vocabulary[testee_id]['non_frequent_words'][word_elem] += 1
                        else:
                            self.vocabulary[testee_id]['non_frequent_words'][word_elem] = 1
        return self.vocabulary[testee_id]

    def get_id(self):
        return self.test_id

    def find_contraction(self, word):
        sentence_array = self.contractions[word].split('/')
        word_array = []
        if len(sentence_array) > 1:
            for elem in sentence_array:
                word_array += elem.split()
        elif len(sentence_array) == 1:
            word_array = sentence_array[0].split()
        return word_array

    def present(self):
        if config.PRESENTATION_WAY == "sqlite":
            self.present_through_sqlite()

    def present_through_sqlite(self):
        for gdm_id in list(self.result_dict.keys()):
            date_time = datetime.datetime.now()
            cursor = aux_functions.conn.cursor()
            test_id = "{}:{}:{}".format(gdm_id, self.test_id, date_time)
            try:
                cursor.execute(
                    """
                    INSERT
                    INTO MLST(test_id, gdm_id, date_time_run)
                    VALUES (?, ?, ?);
                    """,
                    [test_id, gdm_id, date_time]
                )
                # Successful insert
                aux_functions.conn.commit()
            except sqlite3.Error as er:
                # Failed insert.
                print("Error occurred while inserting into MLST-table. Error was {}.".format(er))
            for conv_nbr in self.result_dict[gdm_id]['Conversations']:
                for word in self.result_dict[gdm_id]['Conversations'][conv_nbr]['word_counter']:
                    cursor = aux_functions.conn.cursor()
                    try:
                        cursor.execute(
                            """
                            INSERT
                            INTO MLST2_word_counter(test_id, conv_nbr, word, frequency)
                            VALUES (?, ?, ?, ?);
                            """,
                            [test_id, conv_nbr, word,
                             self.result_dict[gdm_id]['Conversations'][conv_nbr]['word_counter'][word]]
                        )
                        # Successful insert
                        aux_functions.conn.commit()
                    except sqlite3.Error as er:
                        # Failed insert.
                        print(er)

                for word_rank in self.result_dict[gdm_id]['Conversations'][conv_nbr]['frequency_word_list']:
                    cursor = aux_functions.conn.cursor()
                    try:
                        cursor.execute(
                            """
                            INSERT
                            INTO MLST2_frequency_list(test_id, conv_nbr, word_rank, frequency)
                            VALUES (?, ?, ?, ?);
                            """,
                            [test_id, conv_nbr, word_rank,
                             self.result_dict[gdm_id]['Conversations'][conv_nbr]['frequency_word_list'][word_rank]]
                        )
                        # Successful insert
                        aux_functions.conn.commit()
                    except sqlite3.Error as er:
                        # Failed insert.
                        print(er)

                for non_freq_word in self.result_dict[gdm_id]['Conversations'][conv_nbr]['non_frequent_words']:
                    cursor = aux_functions.conn.cursor()
                    try:
                        cursor.execute(
                            """
                            INSERT
                            INTO MLST2_non_frequent_list(test_id, conv_nbr, word, frequency)
                            VALUES (?, ?, ?, ?);
                            """,
                            [test_id, conv_nbr, non_freq_word,
                             self.result_dict[gdm_id]['Conversations'][conv_nbr]['non_frequent_words'][non_freq_word]]
                        )
                        # Successful insert
                        aux_functions.conn.commit()
                    except sqlite3.Error as er:
                        # Failed insert.
                        print(er)


class CoherentResponseTest(AbstractConvTest, ABC):
    """ MLST4 test testing for coherence between two responses."""

    def __init__(self):
        self.test_id = 'MLST4'
        self.bert_type = 'bert-base-uncased'
        self.bert_tokenizer = BertTokenizer.from_pretrained(self.bert_type)
        self.bert_model = BertForNextSentencePrediction.from_pretrained(self.bert_type)
        self.result_dict = {}

    def analyse_conversations(self, conversations: list):
        for i in range(len(conversations)):
            conv = conversations[i]
            results = self.analyse(conv)

            try:
                self.result_dict[conv.get_testee_id()]['Conversations'][int(i + 1)] = results
            except KeyError:
                self.result_dict[conv.get_testee_id()] = {}
                self.result_dict[conv.get_testee_id()]['Conversations'] = {}
                self.result_dict[conv.get_testee_id()]['Conversations'][int(i + 1)] = results
        return self.result_dict

    def analyse(self, conv: Conversation):
        results = list()
        for i in range(1, len(conv)):
            elem = conv[i]
            if elem.get_role() == 'Testee':
                result = {}
                prev_string = str(conv[i - 1])
                testee_string = str(elem)
                next_sent_prediction = self.next_sent_prediction(string1=prev_string, string2=testee_string)
                result['Previous message'] = str(prev_string)
                result['Testee message'] = str(elem)
                result['NSP-prediction'] = next_sent_prediction
                results.append(result)
        return results

    def get_id(self):
        return self.test_id

    def next_sent_prediction(self, string1, string2):
        inputs = self.bert_tokenizer(string1, string2, return_tensors='pt')
        outputs = self.bert_model(**inputs)
        return self.softmax(outputs.logits.tolist()[0])

    @staticmethod
    def softmax(vector):
        e = exp(vector)
        return e / e.sum()

    def present(self):
        if config.PRESENTATION_WAY == "sqlite":
            self.present_through_sqlite()

    def present_through_sqlite(self):
        for gdm_id in list(self.result_dict.keys()):
            date_time = datetime.datetime.now()
            cursor = aux_functions.conn.cursor()
            test_id = "{}:{}:{}".format(gdm_id, self.test_id, date_time)
            try:
                cursor.execute(
                    """
                    INSERT
                    INTO MLST(test_id, gdm_id, date_time_run)
                    VALUES (?, ?, ?);
                    """,
                    [test_id, gdm_id, date_time]
                )
                # Successful insert
                aux_functions.conn.commit()
            except sqlite3.Error as er:
                # Failed insert.
                print("Error occurred while inserting into MLST-table. Error was {}.".format(er))
            for conv_nbr in self.result_dict[gdm_id]['Conversations']:
                for tested_response_dict in self.result_dict[gdm_id]['Conversations'][conv_nbr]:
                    cursor = aux_functions.conn.cursor()
                    try:
                        cursor.execute(
                            """
                            INSERT
                            INTO MLST4_results(test_id, conv_nbr, prev_msg, testee_message, pos_pred, neg_pred)
                            VALUES (?, ?, ?, ?, ?, ?);
                            """,
                            [test_id, conv_nbr, tested_response_dict['Previous message'],
                             tested_response_dict['Testee message'], tested_response_dict['NSP-prediction'][0],
                             tested_response_dict['NSP-prediction'][1]]
                        )
                        # Successful insert
                        aux_functions.conn.commit()
                    except sqlite3.Error as er:
                        # Failed insert.
                        print(er)


class ReadabilityIndexTest(AbstractConvTest, ABC):
    """ MLST2TC2 test testing for readability."""

    def __init__(self):
        self.test_id = 'MLST2TC2'
        self.excluded_tokens = conversation.set_of_excluded_tokens()
        self.result_dict = {}

    def analyse_conversations(self, conversations: list):
        for i in range(len(conversations)):
            conv = conversations[i]
            results = self.analyse(conv)

            try:
                self.result_dict[conv.get_testee_id()]['Conversations'][int(i + 1)] = results
            except KeyError:
                self.result_dict[conv.get_testee_id()] = {}
                self.result_dict[conv.get_testee_id()]['Conversations'] = {}
                self.result_dict[conv.get_testee_id()]['Conversations'][int(i + 1)] = results
        return self.result_dict

    def analyse(self, conv: Conversation):
        results = {
            'amount_sentences': 0,
            'amount_words': 0,
            'amount_words_grt_6': 0
        }
        for message in conv:
            if message.get_role() == 'Testee':
                results['amount_sentences'] += conversation.count_sentences_within_string(str(message))
                results['amount_words'] += len(str(message).split())
                for word in str(message).split():
                    word = conversation.clean_from_excluded_tokens(word)
                    if len(word) > 6:
                        results['amount_words_grt_6'] += 1
        results['readability_index'] = results['amount_words'] / results['amount_sentences'] + \
                                       results['amount_words_grt_6'] / results['amount_words'] * 100
        return results

    def get_id(self):
        return self.test_id

    def present(self):
        if config.PRESENTATION_WAY == "sqlite":
            self.present_through_sqlite()

    def present_through_sqlite(self):
        for gdm_id in list(self.result_dict.keys()):
            date_time = datetime.datetime.now()
            cursor = aux_functions.conn.cursor()
            test_id = "{}:{}:{}".format(gdm_id, self.test_id, date_time)
            try:
                cursor.execute(
                    """
                    INSERT
                    INTO MLST(test_id, gdm_id, date_time_run)
                    VALUES (?, ?, ?);
                    """,
                    [test_id, gdm_id, date_time]
                )
                # Successful insert
                aux_functions.conn.commit()
            except sqlite3.Error as er:
                # Failed insert.
                print("Error occurred while inserting into MLST7-table. Error was {}.".format(er))
            for conv_nbr in self.result_dict[gdm_id]['Conversations']:
                cursor = aux_functions.conn.cursor()
                conv = self.result_dict[gdm_id]['Conversations'][conv_nbr]
                try:
                    cursor.execute(
                        """
                        INSERT
                        INTO MLST2TC2_results(test_id, conv_nbr, amount_sents, amount_words, amount_words_grt_6,
                         readab_index)
                        VALUES (?, ?, ?, ?, ?, ?);
                        """,
                        [test_id, conv_nbr, conv['amount_sentences'], conv['amount_words'], conv['amount_words_grt_6'],
                         conv['readability_index']]
                    )
                    # Successful insert
                    aux_functions.conn.commit()
                except sqlite3.Error as er:
                    # Failed insert.
                    print(er)


# ----------------------- Injected tests
""" Below are the implemented injected tests. """
