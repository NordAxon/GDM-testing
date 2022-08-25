import argparse
import time
import datetime

import config
import src.worlds as worlds

DEBUG_MODE = False


def debug_script_setup(args):
    """If DEBUG_MODE is True, the following settings are used for setting up the script."""
    args.conv_length = config.CONV_LENGTH
    args.amount_convs = config.AMOUNT_CONVS
    args.conv_partner_id = config.CONV_PARTNER_ID
    args.testee_ids = config.TESTEE_IDS
    args.conv_starter = config.CONV_STARTER
    args.verbose = config.VERBOSE
    args.export_channel = config.EXPORT_CHANNEL
    args.read_run_ids = config.READ_RUN_IDS
    args.experiment_id = config.EXPERIMENT_ID
    args.overwrite_db = config.OVERWRITE_TABLE
    args.random_conv_start = config.RANDOM_CONV_START
    args.interview_mode = config.INTERVIEW_MODE
    return args


if __name__ == "__main__":
    """Main-function that initiates the whole script.
    If DEBUG_MODE is specified to be True, you can specify the settings here inside the script so that you may
    debug the code without the use of the CLI."""
    start_time = time.time()

    parser = argparse.ArgumentParser(
        description="Parser for setting up the script as you want"
    )
    if DEBUG_MODE:
        args = parser.parse_args()
        args = debug_script_setup(args)
    else:
        worlds.TestWorld.add_to_argparse(parser)
        args = parser.parse_args()

    if args.verbose:
        print("Test initiated.")

    """ test_world - the test environment setup in which the testing will be performed. """
    start_time_test_world = time.time()
    test_world = worlds.TestWorld(args)
    end_time_test_world = time.time() - start_time_test_world
    if args.verbose:
        print(
            "The setup of test world took {:.2f} seconds / {:.2f} minutes / {:.2f} hours and finished at {}".format(
                end_time_test_world,
                end_time_test_world / 60,
                end_time_test_world / (60 ** 2),
                datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            )
        )

    """If no files are chosen the framework will generate conversations based upon the specified settings,
    otherwise it will read a from txt-files and go direct to evaluating those. """
    start_time_conversations = time.time()
    test_world.init_conversations()
    end_time_convs = time.time() - start_time_conversations
    if args.verbose:
        print(
            "The generation of conversations took {:.2f} seconds / {:.2f} minutes / {:.2f} hours and finished at {}".format(
                end_time_convs,
                end_time_convs / 60,
                end_time_convs / (60 ** 2),
                datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            )
        )

    start_time_tests = time.time()
    test_world.init_tests()
    end_time_tests = time.time() - start_time_tests
    if args.verbose:
        print(
            "The tests took {:.2f} seconds / {:.2f} minutes / {:.2f} hours and finished at {}".format(
                end_time_tests,
                end_time_tests / 60,
                end_time_tests / (60 ** 2),
                datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            )
        )

    start_time_export = time.time()
    test_world.export_results()
    end_time_export = time.time() - start_time_export
    if args.verbose:
        print(
            "The export took {:.2f} seconds / {:.2f} minutes / {:.2f} hours and finished at {}".format(
                end_time_export,
                end_time_export / 60,
                end_time_export / (60 ** 2),
                datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            )
        )

    end_time = time.time() - start_time
    if args.verbose:
        print(
            "The script took {:.2f} seconds / {:.2f} minutes / {:.2f} hours and finished at {}".format(
                end_time,
                end_time / 60,
                end_time / (60 ** 2),
                datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            )
        )
