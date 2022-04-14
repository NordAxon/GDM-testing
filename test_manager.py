import datetime
import sqlite3

import aux_functions
import config
import tests

implemented_tests = {
    'static_tests': {
        'MLST7': tests.ToxicContentTest,
        'MLST2': tests.VocabularySizeTest,
        'MLST4': tests.CoherentResponseTest,
        'MLST2TC2': tests.ReadabilityIndexTest
    },
    'injected_tests': {

    }
}


class TestManager:
    """ Class for handling all the test cases and containing the results. """

    def __init__(self, list_testees, conversations):
        self.test_results = {}
        self.conversations = conversations
        self.testees = list_testees
        if config.EXPORT_CHANNEL == "sqlite":
            self.setup_sqlite()

    def setup_sqlite(self):
        """ Method used for setting up the sqlite-database, which is based upon the table called GDMs. """
        for testee in self.testees:
            cursor = aux_functions.conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT
                    INTO GDMs(gdm_id, date_time)
                    VALUES (?, ?);
                    """,
                    [testee.get_id(), datetime.datetime.now()]
                )

                # Successful insert
                aux_functions.conn.commit()
            except sqlite3.Error as er:
                # Failed insert.
                print(er)

    def init_tests(self):
        """ Central function for initiating all tests. """
        self.init_static_tests()
        self.init_injected_tests()

    def init_static_tests(self):
        """ Method for initiating the static tests, looping over them one by one and running them. """
        for test_case in implemented_tests['static_tests']:
            if config.VERBOSE:
                print("Initiates {}".format(test_case))
            test_case = implemented_tests['static_tests'][test_case]()
            test_case.analyse_conversations(self.conversations)
            self.test_results[test_case] = test_case
            if config.VERBOSE:
                print("Finished")

    def init_injected_tests(self):
        """ Method for initiating the injected tests, which loops over them one by one and first runs the injection and
        then analyses the result. """
        for test_case in implemented_tests['injected_tests']:
            if config.VERBOSE:
                print("Initiates {}".format(test_case))
            test_case.run(self.conversations)
            test_case.analyse(self.conversations)
            if config.VERBOSE:
                print("Finished")

    def export_results(self):
        """ Method for presenting/exporting the results, which per test case calls the method "present()", which per
         case handles how to present/export the results."""
        for test_case in self.test_results:
            if config.VERBOSE:
                print("Transfers test results of {}".format(test_case))
            test_case.present()
            if config.VERBOSE:
                print("Finished")
