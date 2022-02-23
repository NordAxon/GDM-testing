import argparse
import config
import worlds

""" argparse for parsing the input from the CLI. """
parser = argparse.ArgumentParser(description="Parser for setting up the script as you want")
parser.add_argument('-l', '--length-conv-round', metavar='', type=int, help="How many rounds shall there be per "
                                                                            "conversation until restart")
parser.add_argument('-a', '--amount-convs', metavar='', type=int, help="How many conversations shall there be per "
                                                                       "tested GDM")
parser.add_argument('-t', '--tested-gdms', metavar='', type=str, help="Write one or several GDMs you want to test. "
                                                                      "If several, have them separated by ','. ")
parser.add_argument('-cp', '--conv-partner', metavar='', type=str, help="Specify which GDM to test your GDM against")
parser.add_argument('-gd', '--gen-dialog', action="store_true", default=False,
                    help="True: The script generates conversations using the specified GDMs. False: Evaluates a "
                         ".txt-file")
parser.add_argument('-cs', '--conv-starter', metavar='', type=str, help="Testee: testee initiates every conversation."
                                                                        "Conv-partner: the conversation partner "
                                                                        "initiates all conversations."
                                                                        "Not specified: 50-50 per conversation "
                                                                        "who starts that conversation.")
args = parser.parse_args()


def debug_script_setup(args):
    """ If Config.DEBUG is True, the following settings are used for setting up the script. """
    args.length_conv_round = 2
    args.amount_convs = 2
    args.conv_partner = 'Blenderbot90m'
    args.tested_gdms = 'Blenderbot90m,BlendERboT90m'
    args.gen_dialog = True
    return args


if __name__ == "__main__":
    """ Main-function that initiates the whole script. 
    If DEBUG_MODE is specified to be True, you can specify the settings here inside the script so that you may 
    debug the code without the use of the CLI. """
    if config.DEBUG_MODE:
        args = debug_script_setup(args)

    """ test_world - the test environment setup in which the testing will be performed. """
    test_world = worlds.TestWorld()

    """ if args.gen_dialog is set to True, the framework will generate conversations based upon the specified settings,
    otherwise it will read a .txt-file and go direct to evaluating those. """
    if args.gen_dialog:
        test_world.setup_scripts(length_conv_round=args.length_conv_round, amount_convs=args.amount_convs,
                                 tested_gdms=args.tested_gdms, conv_partner=args.conv_partner,
                                 conv_start=args.conv_starter)
        conversation = test_world.init_conversations()
        evaluation = test_world.init_tests(conversation)
    else:
        print('TODO: implement how to read a .txt-file')
