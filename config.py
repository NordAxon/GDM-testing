DEBUG_MODE = True
VERBOSE = True
RANDOM_CONV_START = True
CONV_LENGTH = 8
AMOUNT_CONVS = 5
CONV_PARTNER = 'blenderbot90m'
TESTEE = 'blenderbot400m,blenderbot90m'
GENERATE_DIALOGUE = True
CONV_STARTER = ""

""" How the data should be stored and presented. Either one of ["json", "sql"]. "json" means storing the results as a 
json-object, "sqlite" means writing into a table during the test run."""
PRESENTATION_WAY = "sqlite"
