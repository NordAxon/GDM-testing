# General settings
EXPERIMENT_ID = "EXPERIMENT_ID"
VERBOSE = True
EXPORT_CHANNEL = "sqlite"
OVERWRITE_TABLE = False

# Choose tests to run (can be found in src.test_manager.implemented_tests)
tests_to_run = [
    "TOX",
    "VOCSZ",
    "COHER",
    "READIND",
]

# For generating new conversations
CONV_LENGTH = 2
CONV_STARTER = ""
RANDOM_CONV_START = True
AMOUNT_CONVS = 2
CONV_PARTNER_ID = "blenderbot90m"
TESTEE_IDS = "your_local_model_images"
INTERVIEW_MODE = True

# For reading from files
READ_RUN_IDS = ""
