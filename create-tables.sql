-- Delete the tables if they exist.
-- Disable foreign key checks, so the tables can
-- be dropped in arbitrary order.
PRAGMA foreign_keys=OFF;

DROP TABLE IF EXISTS runs;
DROP TABLE IF EXISTS TOX_results;
DROP TABLE IF EXISTS COHER_results;
DROP TABLE IF EXISTS VOCSZ_frequency_list;
DROP TABLE IF EXISTS VOCSZ_non_frequent_list;
DROP TABLE IF EXISTS READIND_results;
PRAGMA foreign_keys=ON;

-- Create the tables.
CREATE TABLE runs (
    run_id              INT NOT NULL,
    testee_id           TEXT NOT NULL,
    conv_partner_id     TEXT NOT NULL,
    conv_length         INT NOT NULL,
    amount_convs        INT NOT NULL,
    conv_starter        TEXT NOT NULL,
    date_time_generated DATETIME,
    date_time_tested    DATETIME,
    PRIMARY KEY (run_id)
);

CREATE TABLE TOX_results (
    run_id              INT NOT NULL,
    conv_nbr            INT NOT NULL,
    msg_nbr             INT NOT NULL,
    toxicity_type       TEXT NOT NULL,
    toxicity_level      DOUBLE NOT NULL,
    FOREIGN KEY         (run_id) REFERENCES runs(run_id)
);

CREATE TABLE COHER_results (
    run_id              INT NOT NULL,
    conv_nbr            INT NOT NULL,
    msg_nbr             INT NOT NULL,
    neg_pred            DOUBLE NOT NULL,
    FOREIGN KEY         (run_id) REFERENCES runs(run_id)
);

CREATE TABLE VOCSZ_results (
    run_id              INT NOT NULL,
    conv_nbr            INT NOT NULL,
    word                TEXT NOT NULL,
    word_rank           INT NOT NULL,
    frequency           INT NOT NULL,
    FOREIGN KEY         (run_id) REFERENCES runs(run_id)
);

CREATE TABLE READIND_results (
    run_id              INT NOT NULL,
    conv_nbr            INT NOT NULL,
    readab_index        DOUBLE NOT NULL,
    FOREIGN KEY         (run_id) REFERENCES runs(run_id)
);