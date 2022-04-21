import argparse
import time

import config
import worlds


def debug_script_setup():
    """ If Config.DEBUG is True, the following settings are used for setting up the script. """
    args = {}
    args['length_conv_round'] = config.CONV_LENGTH
    args['amount_convs'] = config.AMOUNT_CONVS
    args['conv_partner'] = config.CONV_PARTNER
    args['tested_gdms'] = config.TESTEE
    args['gen_dialog'] = config.GENERATE_DIALOGUE
    args['conv_starter'] = config.CONV_STARTER
    args['verbose'] = config.VERBOSE
    args['export_channel'] = config.EXPORT_CHANNEL
    args["gen_dialog"] = config.GENERATE_DIALOGUE
    return args


if __name__ == "__main__":
    """ Main-function that initiates the whole script. 
    If DEBUG_MODE is specified to be True, you can specify the settings here inside the script so that you may 
    debug the code without the use of the CLI. """
    start_time = time.time()

    if config.VERBOSE:
        print("Test initiated.")
    if config.DEBUG_MODE:
        args = debug_script_setup()
    else:
        parser = argparse.ArgumentParser(description="Parser for setting up the script as you want")
        worlds.TestWorld.add_to_argparse(parser)
        args = parser.parse_args()

    """ test_world - the test environment setup in which the testing will be performed. """
    start_time_test_world = time.time()
    test_world = worlds.TestWorld(args)
    end_time_test_world = time.time() - start_time_test_world
    print("The setup of test world took {:.2f} seconds / {:.2f} minutes / {:.2f} hours"
          .format(end_time_test_world, end_time_test_world / 60, end_time_test_world / (60 ** 2)) if config.VERBOSE
          else print())

    """ if args.gen_dialog is set to True, the framework will generate conversations based upon the specified settings,
    otherwise it will read a .txt-file and go direct to evaluating those. """
    start_time_conversations = time.time()
    test_world.init_conversations()
    end_time_convs = time.time() - start_time_conversations
    print("The generation of conversations took {:.2f} seconds / {:.2f} minutes / {:.2f} hours"
          .format(end_time_convs, end_time_convs / 60, end_time_convs / (60 ** 2)) if config.VERBOSE else print())

    start_time_tests = time.time()
    test_world.init_tests()
    end_time_tests = time.time() - start_time_tests
    print("The tests took {:.2f} seconds / {:.2f} minutes / {:.2f} hours"
          .format(end_time_tests, end_time_tests / 60, end_time_tests / (60 ** 2)) if config.VERBOSE else print())

    start_time_export = time.time()
    test_world.export_results()
    end_time_export = time.time() - start_time_export
    print("The export took {:.2f} seconds / {:.2f} minutes / {:.2f} hours"
          .format(end_time_export, end_time_export / 60, end_time_export / (60 ** 2)) if config.VERBOSE else print())

    end_time = time.time() - start_time
    print("The script took {:.2f} seconds / {:.2f} minutes / {:.2f} hours"
          .format(end_time, end_time / 60, end_time / (60**2)) if config.VERBOSE else print())