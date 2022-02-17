import abc

from conversation import Conversation


class TestPlan():

    def __init__(self):
        pass


class AbstractTestCase(abc.ABC):
    """AbstractTestCase defines an interface for tests that construct a specific conversation.

    E.g. A memory test where a testagent is given certain information and is later asked to remember that information

    """

    def __init__(self):
        pass

    def get_dialog(self):
        return Conversation()

    @abc.abstractmethod
    def run(self) -> Conversation:
        "Runs testcase"
        pass

    @abc.abstractmethod
    def analyse(self) -> Conversation:
        "Performs analysis of outcome"
        pass


class AbstractDialogTest(abc.ABC):
    """A dialogtest is a test that is performed on any given dialog in a static way.

    E.g. a test where every line is tested for grammatical errors, toxicity.
    """

    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def analyse(self, dialog: Conversation):
        """Analyses the dialog
        Args:
            dialog (Dialog): Dialog to analyse
        Returns:
            Dict: Dictionary with metrics produced by test
        """
        pass