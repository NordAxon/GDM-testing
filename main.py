import argparse
import config
import worlds

# argparse for parsing the input from the CLI.
parser = argparse.ArgumentParser(description="Parser for setting up the script as you want")
parser.add_argument('-l', '--length-conv-round', metavar='', type=int, help="How many rounds shall there be per "
                                                                            "conversation until restart")
parser.add_argument('-a', '--amount-convs', metavar='', type=int, help="How many conversations shall there be per "
                                                                       "tested GDM")
parser.add_argument('-t', '--tested-gdms', metavar='', type=str, help="Write one or several GDMs you want to test. "
                                                                      "If several, have them separated by ','. ")
parser.add_argument('-cp', '--conv-partner', metavar='', type=str, help="Specify which GDM to test your GDM against")
args = parser.parse_args()

if __name__ == "__main__":
    if config.DEBUG_MODE:
        args.length_conv_round = 20
        args.amount_convs = 20
        args.tested_gdms = 'Blenderbot90m'
        args.conv_partner = 'Blenderbot90m'
    test_world = worlds.TestWorld()
    test_world.setup_scripts(length_conv_round=args.length_conv_round, amount_convs=args.amount_convs,
                             tested_gdms=args.tested_gdms, conv_partner=args.conv_partner)
