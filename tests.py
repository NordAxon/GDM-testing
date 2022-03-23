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
    """ MLST2 test testing for different kinds of toxic contents in a string."""

    def __init__(self):
        self.test_id = 'MLST2'
        self.vocabulary = {
            'Testee': {},
            'Other agent': {},
            'generator': {}
        }
        self.excluded_words_tokens = {
            'words': [],
            'tokens': [
                ',',
                '.',
                '?',
                '!'
            ]
        }

    def analyse(self, conversation: Conversation):
        """ Function for storing words used by the GDM to keep track of its vocabulary.

        Loops over all messages and per message, it splits it in order to isolate the words used. Then it removed
        tokens such as ',', '.', '?', '!'. After these processes, it is added to the dict, either adds 1 to the amount
        of usages for that word, or sets it to one if it is a new word. """
        for elem in conversation:
            role_gdm = elem.get_role()
            word_array = str(elem).split()
            for word in word_array:
                if word[-1] in self.excluded_words_tokens['tokens']:
                    word = word[:-1]

                try:
                    self.vocabulary[role_gdm][word] = self.vocabulary[word] + 1
                except KeyError:
                    self.vocabulary[role_gdm][word] = 1
        return self.vocabulary

    def get_id(self):
        return self.test_id


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
