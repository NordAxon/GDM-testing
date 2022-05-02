DEBUG_MODE = False
VERBOSE = True
RANDOM_CONV_START = True
CONV_LENGTH = 2
AMOUNT_CONVS = 1
CONV_PARTNER = 'blenderbot90m'
TESTEE = 'emely02,emely03'
GENERATE_DIALOGUE = True
CONV_STARTER = ""
OVERWRITE_TABLE = True
LOG_CONVERSATION = True

""" How the data should be stored and presented. Either one of ["sqlite"]. "sqlite" means writing into a table during 
the test run. Currently only support for sqlite. """
EXPORT_CHANNEL = "sqlite"
INTERNAL_STORAGE_CHANNEL = "json"