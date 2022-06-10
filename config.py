DEBUG_MODE = False
VERBOSE = True
RANDOM_CONV_START = True
CONV_LENGTH = 10
AMOUNT_CONVS = 5
CONV_PARTNER = "blenderbot400m"
TESTEE = "emely05"
READ_FILE_NAME = ""
CONV_STARTER = ""
OVERWRITE_TABLE = True
LOG_CONVERSATION = True

""" Through which channel should the data be exported. Either one of ["sqlite"]. "sqlite" means writing into a 
sqlite-table during the test run. Currently only support for sqlite. """
EXPORT_CHANNEL = "sqlite"

""" How the data should be internally stored. Either one of ["json", "dataframes"]. json implicates that all data is 
stored in a json-format and then exported. dataframes means that the data is stored in dataframes, which then uses the
proprietary methods of pandas to export the data into the chosen EXPORT_CHANNEL. """
INTERNAL_STORAGE_CHANNEL = "json"
