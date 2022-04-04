import tests
import os
import sqlite3

implemented_tests = {
    'static_tests': {
        'MLST7': tests.ToxicContentTest,
        'MLST4': tests.CoherentResponseTest,
        'MLST2': tests.VocabularySizeTest,
        'MLST2TC2': tests.ReadabilityIndexTest
    },
    'injected_tests': {

    }
}


class TestManager:

    def __init__(self, list_testees, conversations):
        self.test_results = {}
        self.conversations = conversations
        self.testees = list_testees

    def init_tests(self):
        self.init_static_tests()
        self.init_injected_tests()

    def init_static_tests(self):
        for elem in implemented_tests['static_tests']:
            test_case = implemented_tests['static_tests'][elem]()
            self.test_results[elem] = test_case.analyse_conversations(self.conversations)

    def init_injected_tests(self):
        for elem in implemented_tests['injected_tests']:
            elem.run(self.conversations)
            elem.analyse(self.conversations)

    def present_results(self):
        print(self.test_results)

        for elem in implemented_tests['static_tests']:
            test_case = self.test_results[elem]


base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "test_results.sqlite")
conn = sqlite3.connect(db_path)


