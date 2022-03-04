import abc
from abc import ABC

import torch.cuda
from detoxify import Detoxify

from conversation import Conversation


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

# ----------------------- Injected tests
""" Below are the implemented injected tests. """
