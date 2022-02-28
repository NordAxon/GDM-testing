import argparse
import config
import worlds


def debug_script_setup():
    """ If Config.DEBUG is True, the following settings are used for setting up the script. """
    args = {}
    args['length_conv_round'] = 2
    args['amount_convs'] = 2
    args['conv_partner'] = 'Blenderbot90m'
    args['tested_gdms'] = 'Blenderbot90m,BlendERboT90m'
    args['gen_dialog'] = True
    args['conv_starter'] = ""
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
    conversations = []
    if config.GENERATE_DIALOGUE:
        conversations = test_world.init_conversations()
    else:
        print('TODO: implement how to read a .txt-file')
    evaluation = test_world.init_tests(conversations)
