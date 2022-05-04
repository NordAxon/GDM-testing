-- Delete the tables if they exist.
-- Disable foreign key checks, so the tables can
-- be dropped in arbitrary order.
PRAGMA foreign_keys=OFF;

DROP TABLE IF EXISTS GDMs;
DROP TABLE IF EXISTS test_cases;
DROP TABLE IF EXISTS TOX_results;
DROP TABLE IF EXISTS COHER_results;
DROP TABLE IF EXISTS VOCSZ_frequency_list;
DROP TABLE IF EXISTS VOCSZ_non_frequent_list;
DROP TABLE IF EXISTS READIND_results;
PRAGMA foreign_keys=ON;

-- Create the tables.
CREATE TABLE GDMs (
    gdm_id      TEXT NOT NULL,
    date_time   DATETIME,
    PRIMARY KEY (gdm_id)
);

CREATE TABLE test_cases (
    test_id         TEXT DEFAULT (lower(hex(randomblob(16)))),
    gdm_id          TEXT NOT NULL,
    date_time_run   DATETIME,
    PRIMARY KEY     (test_id),
    FOREIGN KEY     (gdm_id) REFERENCES GDMs(gdm_id)
);

CREATE TABLE TOX_results (
    test_id         TEXT DEFAULT (lower(hex(randomblob(16)))),
    conv_nbr        INT NOT NULL,
    toxicity_type   TEXT NOT NULL,
    toxicity_level  DOUBLE NOT NULL,
    FOREIGN KEY     (test_id) REFERENCES test_cases(test_id)
);

CREATE TABLE COHER_results (
    test_id         TEXT DEFAULT (lower(hex(randomblob(16)))),
    conv_nbr        INT NOT NULL,
    neg_pred        DOUBLE NOT NULL,
    FOREIGN KEY     (test_id) REFERENCES test_cases(test_id)
);

CREATE TABLE VOCSZ_frequency_list (
    test_id         TEXT DEFAULT (lower(hex(randomblob(16)))),
    conv_nbr        INT NOT NULL,
    word            TEXT NOT NULL,
    word_rank       INT NOT NULL,
    frequency       INT NOT NULL,
    FOREIGN KEY     (test_id) REFERENCES test_cases(test_id)
);

CREATE TABLE VOCSZ_non_frequent_list (
    test_id         TEXT DEFAULT (lower(hex(randomblob(16)))),
    conv_nbr        INT NOT NULL,
    word            TEXT NOT NULL,
    frequency       INT NOT NULL,
    FOREIGN KEY     (test_id) REFERENCES test_cases(test_id)
);

CREATE TABLE READIND_results (
    test_id             TEXT DEFAULT (lower(hex(randomblob(16)))),
    conv_nbr            INT NOT NULL,
    readab_index        DOUBLE NOT NULL,
    FOREIGN KEY         (test_id) REFERENCES test_cases(test_id)
);