import tests
import copy

implemented_tests = {
    'static_tests': {
        'MLST7': tests.ToxicContentTest,
        'MLST2': tests.VocabularySizeTest,
        'MLST4': tests.CoherentResponseTest
    },
    'injected_tests': {

    }
}


class TestManager:

    def __init__(self, list_testees, conversations):
        self.test_results = {}
        self.conversations = conversations
        self.setup_test_manager(list_testees=list_testees)

    def setup_test_manager(self, list_testees):
        list_keys_static = list(implemented_tests['static_tests'].keys())
        list_keys_injected = list(implemented_tests['injected_tests'].keys())
        for elem in list_testees:
            self.test_results[elem.get_id()] = copy.deepcopy(implemented_tests)

            for test_case in list_keys_static:
                self.test_results[elem.get_id()]['static_tests'][test_case] = {}

            for test_case in list_keys_injected:
                self.test_results[elem.get_id()]['injected_tests'][test_case] = {}

    def init_tests(self):
        self.init_static_tests()
        self.init_injected_tests()

    def init_static_tests(self):
        for elem in implemented_tests['static_tests']:
            test_case = implemented_tests['static_tests'][elem]()
            for i in range(len(self.conversations)):
                conv = self.conversations[i]
                results = test_case.analyse(conv)
                self.test_results[conv.get_testee_id()]['static_tests'][elem]['Conv{}'.format(i + 1)] = results

    def init_injected_tests(self):
        for elem in implemented_tests['injected_tests']:
            elem.run(self.conversations)
            elem.analyse(self.conversations)

    def present_results(self):
        print(self.test_results)
