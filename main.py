import argparse
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
    return args


if __name__ == "__main__":
    """ Main-function that initiates the whole script. 
    If DEBUG_MODE is specified to be True, you can specify the settings here inside the script so that you may 
    debug the code without the use of the CLI. """
    if config.DEBUG_MODE:
        args = debug_script_setup()
    else:
        parser = argparse.ArgumentParser(description="Parser for setting up the script as you want")
        worlds.TestWorld.add_to_argparse(parser)
        args = parser.parse_args()

    """ test_world - the test environment setup in which the testing will be performed. """
    test_world = worlds.TestWorld(args)

    """ if args.gen_dialog is set to True, the framework will generate conversations based upon the specified settings,
    otherwise it will read a .txt-file and go direct to evaluating those. """
    test_world.init_conversations()
    test_world.init_tests()
    test_world.present_results()
