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

from nltk.tokenize import RegexpTokenizer


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
        """ Method for applying the test case to all the produced conversations. More specifically, it loops over all
        conversations, applies the analysis to every conversation and then stores the result in a dict which is
        returned. """
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
        """ Method for applying the detoxifyer to all of testee's messages, and returns the scores."""
        results = self.detoxify.predict(conv.filter_mgs(role="Testee"))
        return results

    def get_id(self):
        """ Method for returning the id of this test. """
        return self.test_id

    def present(self):
        """ The way of which the results should be presented through. """
        if config.EXPORT_CHANNEL == "sqlite":
            self.present_through_sqlite()

    def present_through_sqlite(self):
        """ The method on how to export/present the data using sqlite.

            First, it loops over all the GDMs that have been tested, inserting into MLST that that GDM has been tested,
            with its corresponding test_id, gdm_id and datetime of the run.
        """
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

            """ Secondly, the method loops over all the different conversations. Per conversation, the prediction on
            seven toxic types have been produced. Thus, it loops over those, and ultimately it loops over all the values
            per toxicity type, which is the value per message produced. """
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
        self.frequency_dict_word2rank = self.read_frequency_dict()
        self.frequency_dict_rank2word = self.read_frequency_dict_rank2word()
        self.result_dict = {}
        self.token_indicating_removal = "%%"

    @staticmethod
    def specify_contractions():
        """ Method for specifying/declaring all contractions. That is "it's" = "it is" / "it has" etc."""
        return contractions.contractions

    @staticmethod
    def read_frequency_dict():
        """ Method for setting up the frequency list-dict, which is then used as basis for the whole tests, stating
        which words that have which rankings. """
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

    @staticmethod
    def read_frequency_dict_rank2word():
        """ Method for setting up the frequency list-dict with a mapping from a rank to a word, stating which ranks
        correspond with which words. """
        with open('miscellaneous .txt-files/count_1w.txt') as f:
            lines = f.readlines()

        lines = [elem.split('\t', 1) for elem in lines]

        for elem in lines:
            elem[1] = elem[1][:-2]

        for i in range(len(lines)):
            lines[i] = lines[i][0]
        return lines

    def analyse_conversations(self, conversations: list):
        """ Analyses all the conversations. Every conversation is analysed and the results are added to the results
        dict, which is then returned. """
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


    def analyse2(self, conv: Conversation):
        "My attempt at a quicker version /Alex "
        def is_testee(message: Message):
            return message.agent_id == "Testee"

        # Creates a generator of messages and joins them into one large string which is then lowered
        testee_messages = filter(lambda x: is_testee(x), conv)
        testee_strings = (str(m) for m in testee_messages)
        testee_text = ' '.join(testee_strings).lower()


        # Tokenizer that matches word characters and apostrophes
        tokenizer = RegexpTokenizer(r"[\w']+")
        spans = tokenizer.span_tokenize(testee_text)
        rawtokens = (testee_text[begin : end] for (begin, end) in spans)

        def get_words(tokens):
            "Checks for contradictions"
            for token in tokens:
                # Token is a contracted word
                if token in self.contractions.keys():
                    words = self.contractions[token].split("/")[0]
                    for word in words.split(" "):
                        yield word
                else:
                    yield token
                    
        word_gen = get_words(rawtokens)
        counter = Counter(word_gen)

        # Split the words into different ranks or whatever
        return counter



    def analyse(self, conv: Conversation):
        """ Function for storing words used by the GDM to keep track of its vocabulary.
        Loops over all messages and per message, it splits it in order to isolate the words used. Then it removed
        tokens such as ',', '.', '?', '!'. After these processes, it is added to the dict, either adds 1 to the amount
        of usages for that word, or sets it to one if it is a new word. """
        testee_id = conv.get_testee_id()

        self.vocabulary[testee_id] = {
            'word_counter': Counter(),
            'frequency_word_list': {},
            'non_frequent_words': Counter()
        }

        """ Loops over the messages in the conversation. Per message, it is first checked for whether it belongs to the
        testee or not. It continues only if it belongs to the testee."""
        for message in conv:
            if message.get_role() != "Testee":
                continue
            word_array = str(message).split()
            word_array = self.preprocess_word_array(word_array)

            """ The one or several words that word_array may contain is counted and then added to the existing counter. 
            """
            counter = Counter(word_array)
            self.vocabulary[testee_id]['word_counter'] += counter

            """ Calling the method that adds any word to the frequency list. """
            self.add_to_freq_list(word_array, testee_id)
        return self.vocabulary[testee_id].copy()

    def preprocess_word_array(self, word_array):
        """ Method for preprocessing word_array so that it is ready to be inserted into a Counter for counting the
        frequency per word. Removes tokens defined in the constructor from strings, and if the word is defined in the
        constructor as an "excluded" word, it is not counted. If it is an contraction, it is prolonged to the full
        meaning of the contraction. It is done by copying the array, then adding the correct words to the copy and
        replacing the faulty words with self.token_indicating_removal, whose spots are removed in the end of this
        function. """
        fixed_word_array = word_array.copy()
        for i in range(len(word_array)):
            word = word_array[i]
            word = word.lower()
            word = conversation.clean_from_excluded_tokens(word)
            if word in self.excluded_words or word in self.excluded_tokens:
                fixed_word_array[i] = self.token_indicating_removal
                continue

            """ If the word is a contraction, its full meaning is found and inserted word-wise into the list called 
            word. If no contraction, the word is just inserted into the list. """
            if word in self.contractions:
                word = self.find_contraction(word)
                for word_part in word:
                    fixed_word_array.append(word_part)
                fixed_word_array[i] = self.token_indicating_removal
                continue
            fixed_word_array[i] = word

        while "%%" in fixed_word_array:
            fixed_word_array.remove(self.token_indicating_removal)
        return fixed_word_array

    def add_to_freq_list(self, word_list, testee_id):
        """ Per word that may occur in word_list, the frequency list is also updated. That is the mapping from a
        rank to a frequency. If it does not exist in the frequency list, it is added to the non-frequent
        words-list, which means that the word did not exist in the current frequency list, meaning that it is
        irregular. """
        for word in word_list:
            try:
                """ Fetching the rank may cause KeyError if the specific word is non-existent in the frequency list. """
                rank = self.frequency_dict_word2rank[word]['rank']
                self.vocabulary[testee_id]['frequency_word_list'][rank] = \
                    self.vocabulary[testee_id]['word_counter'][word]
            except KeyError:
                """ Adds the counter to the existing counter in the non-frequent word list"""
                word_counter = Counter([word])
                self.vocabulary[testee_id]['non_frequent_words'] += word_counter

    def get_id(self):
        """ Returns the ID of this test. """
        return self.test_id

    def find_contraction(self, word):
        """ Whenever a word is a contraction, this method finds its full meaning, which may be one or several
        expressions. """
        sentence_array = self.contractions[word].split('/')
        word_array = []
        if len(sentence_array) > 1:
            for elem in sentence_array:
                word_array += elem.split()
        elif len(sentence_array) == 1:
            word_array = sentence_array[0].split()
        return word_array

    def present(self):
        """ Method for presenting the results. """
        if config.EXPORT_CHANNEL == "sqlite":
            self.present_through_sqlite()

    def present_through_sqlite(self):
        """ Method for specifying how to export/present the results. Loops over the GDMs and per GDM transfers the
        test results into the sqlite-file. """
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

            """ Per conversation, it loops over the words that were counted in that conversation. Per word, the word
            and its frequency in that conversation is transferred to the sqlite-database. """
            for conv_nbr in self.result_dict[gdm_id]['Conversations']:
                """ Per word rank that was logged from the test results, one unit is added times the frequency. This is
                in order to fit the Grafana-way of producing histograms. """
                for word_rank in self.result_dict[gdm_id]['Conversations'][conv_nbr]['frequency_word_list']:
                    for i in range(
                            self.result_dict[gdm_id]['Conversations'][conv_nbr]['frequency_word_list'][word_rank]):
                        cursor = aux_functions.conn.cursor()

                        """ Reads the word combined with the word_rank, with the purpose of clarification in the db, if
                        the user would like to double-check any word's frequency or whatever the reason. """
                        word = self.frequency_dict_rank2word[word_rank - 1]
                        try:
                            cursor.execute(
                                """
                                INSERT
                                INTO MLST2_frequency_list(test_id, conv_nbr, word, word_rank, frequency)
                                VALUES (?, ?, ?, ?, ?);
                                """,
                                [test_id, conv_nbr, word, word_rank, 1]
                            )
                            # Successful insert
                            aux_functions.conn.commit()
                        except sqlite3.Error as er:
                            # Failed insert.
                            print(er)

                """ Also, the non-frequent words are transferred to make this data available as well. """
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
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.test_id = 'MLST4'
        self.bert_type = 'bert-base-uncased'
        self.bert_tokenizer = BertTokenizer.from_pretrained(self.bert_type)
        self.bert_model = BertForNextSentencePrediction.from_pretrained(self.bert_type).to(self.device)
        self.result_dict = {}

    def analyse_conversations(self, conversations: list):
        """ Loops over all conversations, it analyses each conversation, and then it adds the results to the results
        dict."""
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
        """ Per conversation, the test case is performed. It produces a list of dicts, where every dict contains the two
        compared messages, along with its NSP-prediction. """
        results = list()
        messages_testee = conv.filter_mgs("Testee")
        messages_other_agent = conv.filter_gdm_preceding_mgs()
        ns_predictions = self.batch_nsp(first_sentences=messages_other_agent, second_sentences=messages_testee)
        for i in range(1, len(conv) - 1):
            message = conv[i]
            if message.get_role() == 'Testee':
                result = {}
                prev_message = str(conv[i - 1])
                testee_message = str(message)

                """ Pops out the index 0-element since that belongs to the currently analyzed pair of messages. Then, we 
                extract element 0 from that list, since we only need the positive prediction. """
                next_sent_prediction = ns_predictions.pop(0)[0]
                result['Previous message'] = str(prev_message)
                result['Testee message'] = str(testee_message)
                result['NSP-prediction'] = next_sent_prediction
                results.append(result)
        return results

    def get_id(self):
        return self.test_id

    def next_sent_prediction(self, string1, string2):
        """ Method for predicting whether string2 coherently follows string1 or not, using NSP-BERT. """
        inputs = self.bert_tokenizer(string1, string2, return_tensors='pt')
        outputs = self.bert_model(**inputs)
        return self.softmax(outputs.logits.tolist()[0])

    def batch_nsp(self, first_sentences: list, second_sentences: list):
        """ Method for assessing NSP between two lists of sentences, with the purpose of improving the performance of
        the test rather than NSP-analyzing message-wise. """
        text_pairs = [(first, second) for first, second in zip(first_sentences, second_sentences)]
        encodings = self.bert_tokenizer.batch_encode_plus(text_pairs, return_tensors="pt", padding=True).to(self.device)
        outputs = self.bert_model(**encodings)
        probs = outputs.logits.softmax(dim=-1)
        return probs.tolist()

    @staticmethod
    def softmax(vector):
        """ Softmax-function for interpreting the logits produced by NSP-BERT. """
        e = exp(vector)
        return e / e.sum()

    def present(self):
        if config.EXPORT_CHANNEL == "sqlite":
            self.present_through_sqlite()

    def present_through_sqlite(self):
        """ Method for exporting/presenting the results of this test into the sqlite-database. Per GDM, it inserts info
        about which test that was performed on which GDM and at what datetime. """
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

            """ Per conversation and per test result, the previous and the tested message is inserted into the database,
            along with the positive and negative predictions."""
            for conv_nbr in self.result_dict[gdm_id]['Conversations']:
                for tested_response_dict in self.result_dict[gdm_id]['Conversations'][conv_nbr]:
                    cursor = aux_functions.conn.cursor()
                    try:
                        cursor.execute(
                            """
                            INSERT
                            INTO MLST4_results(test_id, conv_nbr, neg_pred)
                            VALUES (?, ?, ?);
                            """,
                            [test_id, conv_nbr, 1 - tested_response_dict['NSP-prediction']]
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
        """ Applies this test on all the conversations and then adds the results to the result dict. """
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
        """ Per conversation, the test is applied and the results are stored. """
        results = {
            'amount_sentences': 0,
            'amount_words': 0,
            'amount_words_grt_6': 0
        }

        """ Loops over all messages, and per message it stores the amount of sentences, the amount of words and the 
        amount of words greater than six. Then, the readability index is calculated according to a formula."""
        for message in conv:
            if message.get_role() == 'Testee':
                results['amount_sentences'] += conversation.count_sentences_within_string(str(message))
                for word in str(message).split():
                    word = conversation.clean_from_excluded_tokens(word)

                    """ word needs to be no excluded token and longer than 0. That is since if the GDM has produced this
                    sentence as an example: "Hello , how are you today ?", then .clean_from_excluded_tokens would return 
                    "" given "," or "?" as input, which should be disregarded. """
                    if word not in self.excluded_tokens and len(word) > 0:
                        results['amount_words'] += 1
                    if len(word) > 6:
                        results['amount_words_grt_6'] += 1
        results['readability_index'] = results['amount_words'] / results['amount_sentences'] + \
                                       results['amount_words_grt_6'] / results['amount_words'] * 100
        return results

    def get_id(self):
        return self.test_id

    def present(self):
        if config.EXPORT_CHANNEL == "sqlite":
            self.present_through_sqlite()

    def present_through_sqlite(self):
        """ Method for transferring the test results into the database. More specifically, it loops over all GDMs, then
        checks per conversation what the different metrics were, and then inserts those into the database. """
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
                        INTO MLST2TC2_results(test_id, conv_nbr, readab_index)
                        VALUES (?, ?, ?);
                        """,
                        [test_id, conv_nbr, conv['readability_index']]
                    )
                    # Successful insert
                    aux_functions.conn.commit()
                except sqlite3.Error as er:
                    # Failed insert.
                    print(er)


# ----------------------- Injected tests
""" Below are the implemented injected tests. """
