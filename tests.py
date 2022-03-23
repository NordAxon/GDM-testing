import abc
from abc import ABC

import torch.cuda
from detoxify import Detoxify
from transformers import BertTokenizer, BertForNextSentencePrediction

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
    def analyse(self, conversation: Conversation):
        """Analyses the dialog
        Args:
            conversation (Conversation): Conversation to analyse
        Returns:
            Dict: Dictionary with metrics produced by test
        """
        pass


# ----------------------- Conversation tests
""" Below are the implemented conversation tests. """


class ToxicContentTest(AbstractConvTest, ABC):
    """ MLST7 test testing for different kinds of toxic contents in a string."""

    def __init__(self):
        self.test_id = 'MLST7'
        self.detoxify = Detoxify('original', device='cuda') if torch.cuda.is_available() else \
            Detoxify('original', device='cpu')

    def analyse(self, conversation: Conversation):
        results = self.detoxify.predict(conversation.str_conversation())
        return results

    def get_id(self):
        return self.test_id


class VocabularySizeTest(AbstractConvTest, ABC):
    """ """

    def __init__(self):
        self.test_id = 'MLST2'
        self.vocabulary = {}
        self.excluded_words_tokens = {
            'words': [],
            'tokens': [
                ',',
                '.',
                '?',
                '!'
            ]
        }
        self.frequency_dict = self.read_frequency_dict()

    def analyse(self, conversation: Conversation):
        """ Function for storing words used by the GDM to keep track of its vocabulary.

        Loops over all messages and per message, it splits it in order to isolate the words used. Then it removed
        tokens such as ',', '.', '?', '!'. After these processes, it is added to the dict, either adds 1 to the amount
        of usages for that word, or sets it to one if it is a new word. """
        testee_id = conversation.get_testee_id()
        if testee_id not in self.vocabulary:
            self.vocabulary[conversation.get_testee_id()] = {}

        for elem in conversation:
            if elem.get_role() != "Testee":
                continue
            word_array = str(elem).split()
            for word in word_array:
                """ Removes tokens defined in the constructor from strings, and if the word is defined in the 

                constructor as an "excluded" word, it is not counted. """
                if word[-1] in self.excluded_words_tokens['tokens']:
                    word = word[:-1]
                if word in self.excluded_words_tokens['words']:
                    continue

                try:
                    self.vocabulary[testee_id][word] = self.vocabulary[word] + 1
                except KeyError:
                    self.vocabulary[testee_id][word] = 1
        return self.vocabulary[testee_id]

    def get_id(self):
        return self.test_id

    @staticmethod
    def read_frequency_dict():
        with open('count_1w.txt') as f:
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


class CoherentResponseTest(AbstractConvTest, ABC):
    """ MLST4 test testing for different kinds of toxic contents in a string."""

    def __init__(self):
        self.test_id = 'MLST4'
        self.bert_type = 'bert-base-uncased'
        self.bert_tokenizer = BertTokenizer.from_pretrained(self.bert_type)
        self.bert_model = BertForNextSentencePrediction.from_pretrained(self.bert_type)

    def analyse(self, conversation: Conversation):
        results = list()
        for i in range(1, len(conversation)):
            elem = conversation[i]
            if elem.get_role() == 'Testee':
                result = {}
                prev_string = str(conversation[i - 1])
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
        return outputs.logits.tolist()[0]

# ----------------------- Injected tests
""" Below are the implemented injected tests. """
