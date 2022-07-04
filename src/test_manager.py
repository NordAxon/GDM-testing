from datetime import datetime
from sqlite3 import Error
import time
import src.aux_functions as af
from pathlib import Path
import json
from src import tests
from config import tests_to_run


implemented_tests = {
    "static_tests": {
        "TOX": tests.ToxicContentTest,
        "VOCSZ": tests.VocabularySizeTest,
        "COHER": tests.CoherentResponseTest,
        "READIND": tests.ReadabilityIndexTest,
    },
    "injected_tests": {},
}


class TestManager:
    """Class for handling all the test cases and containing the results."""

    def __init__(self, testee_ids, conversations, args):
        self.args = args
        self.test_results = {}
        self.conversations = conversations
        self.testee_ids = testee_ids

        with open(
            Path(__file__).parents[1].resolve()
            / f"test_data/{self.args.experiment_id}/experiment_config.json",
            "r",
        ) as f:
            config = json.load(f)
            self.config = {int(k): v for k, v in config.items()}

        if args.export_channel == "sqlite":
            self.db_path = af.create_sqlite(args)
            self.setup_sqlite()

    def setup_sqlite(self):
        """Method used for setting up the sqlite-database, which is based upon the table called GDMs."""
        for run_id, _ in self.conversations.items():
            conn = af.create_connection(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT run_id FROM runs WHERE run_id = ?", (run_id,))
                data = cursor.fetchall()
                if len(data) == 0:
                    cursor.execute(
                        """
                        INSERT
                        INTO runs(run_id, testee_id, conv_partner_id, conv_length, amount_convs, conv_starter, date_time_generated, date_time_tested)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        [
                            run_id,
                            self.config[run_id]["testee_id"],
                            self.config[run_id]["conv_partner_id"],
                            self.config[run_id]["conv_length"],
                            self.config[run_id]["amount_convs"],
                            self.config[run_id]["conv_starter"],
                            self.config[run_id]["date_time_generated"],
                            datetime.utcnow(),
                        ],
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE runs
                        SET date_time_tested=?;
                        """,
                        [datetime.utcnow(),],
                    )

                # Successful insert
                conn.commit()
            except Error as e:
                print(e)
            finally:
                af.close_connection(conn)

    def init_tests(self):
        """Central function for initiating all tests."""
        self.init_static_tests()
        self.init_injected_tests()

    def init_static_tests(self):
        """Method for initiating the static tests, looping over them one by one and running them."""
        for test_case in implemented_tests["static_tests"]:
            if self.args.verbose:
                print("Initiating {}".format(test_case))
                start_time_tc = time.time()
            test_case = implemented_tests["static_tests"][test_case]()
            test_case.analyse_conversations(self.conversations)
            self.test_results[test_case] = test_case
            if self.args.verbose:
                end_time_tc = time.time() - start_time_tc
                print(
                    "The test case took {:.2f} seconds / {:.2f} minutes / {:.2f} hours and finished at {}".format(
                        end_time_tc,
                        end_time_tc / 60,
                        end_time_tc / (60 ** 2),
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    )
                )

    def init_injected_tests(self):
        """Method for initiating the injected tests, which loops over them one by one and first runs the injection and
        then analyses the result."""
        for test_case in implemented_tests["injected_tests"]:
            if test_case in tests_to_run:
                if self.args.verbose:
                    print("Initiates {}".format(test_case))
                    start_time_tc = time.time()
                test_case.run(self.conversations)
                test_case.analyse(self.conversations, self.db_path)
                if self.args.verbose:
                    end_time_tc = time.time() - start_time_tc
                    print(
                        "The script took {:.2f} seconds / {:.2f} minutes / {:.2f} hours and finished at {}".format(
                            end_time_tc,
                            end_time_tc / 60,
                            end_time_tc / (60 ** 2),
                            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        )
                    )

    def export_results(self):
        """Method for presenting/exporting the results, which per test case calls the method "present()", which per
        case handles how to present/export the results."""
        for test_case in self.test_results:
            if self.args.verbose:
                print("Initiates {}".format(test_case))
                start_time_tc = time.time()
            test_case.export_json_to_sqlite(self.db_path)
            if self.args.verbose:
                end_time_export = time.time() - start_time_tc
                print(
                    "Finished. The export took {:.2f} seconds / {:.2f} minutes / {:.2f} hours and finished at {}".format(
                        end_time_export,
                        end_time_export / 60,
                        end_time_export / (60 ** 2),
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    )
                )
