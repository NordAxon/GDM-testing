import tests

implemented_tests = {
    'static_tests': {
        'MLST7': tests.ToxicContentTest
    },
    'injected_tests': {

    }
}


class TestManager:

    def __init__(self, conversations):
        self.tests = implemented_tests
        self.conversations = conversations

    def init_tests(self):
        self.init_static_tests()
        self.init_injected_tests()

    def init_static_tests(self):
        for elem in self.tests['static_tests']:
            test_case = self.tests['static_tests'][elem]()
            self.tests['static_tests'][elem] = {}
            for i in range(len(self.conversations)):
                conv = self.conversations[i]
                toxicities = test_case.analyse(conv)
                self.tests['static_tests'][elem]['Conv{}'.format(i + 1)] = toxicities

    def init_injected_tests(self):
        for elem in self.tests['injected_tests']:
            elem.run(self.conversations)
            elem.analyse(self.conversations)
