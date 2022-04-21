DEBUG_MODE = False
VERBOSE = True
RANDOM_CONV_START = True
CONV_LENGTH = 3
AMOUNT_CONVS = 2
CONV_PARTNER = 'blenderbot90m'
TESTEE = 'emely02,blenderbot90m,blenderbot400m'
GENERATE_DIALOGUE = True
CONV_STARTER = ""
OVERWRITE_TABLE = True

""" How the data should be stored and presented. Either one of ["sqlite"]. "json" means storing the results as a 
json-object, "sqlite" means writing into a table during the test run. Currently only support for sqlite. """
EXPORT_CHANNEL = "sqlite"
