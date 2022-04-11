-- Delete the tables if they exist.
-- Disable foreign key checks, so the tables can
-- be dropped in arbitrary order.
PRAGMA foreign_keys=OFF;

DROP TABLE IF EXISTS GDMs;
DROP TABLE IF EXISTS MLST;
DROP TABLE IF EXISTS MLST7_results;
DROP TABLE IF EXISTS MLST4_results;
DROP TABLE IF EXISTS MLST2_word_counter;
DROP TABLE IF EXISTS MLST2_frequency_list;
DROP TABLE IF EXISTS MLST2_non_frequent_list;
DROP TABLE IF EXISTS MLST2TC2_results;
PRAGMA foreign_keys=ON;

-- Create the tables.
CREATE TABLE GDMs (
    gdm_id      TEXT NOT NULL,
    date_time   DATETIME,
    PRIMARY KEY (gdm_id)
);

CREATE TABLE MLST (
    test_id         TEXT DEFAULT (lower(hex(randomblob(16)))),
    gdm_id          TEXT NOT NULL,
    date_time_run   DATETIME,
    PRIMARY KEY     (test_id),
    FOREIGN KEY     (gdm_id) REFERENCES GDMs(gdm_id)
);

CREATE TABLE MLST7_results (
    test_id         TEXT DEFAULT (lower(hex(randomblob(16)))),
    conv_nbr        INT NOT NULL,
    toxicity_type   TEXT NOT NULL,
    toxicity_level  DOUBLE NOT NULL,
    FOREIGN KEY     (test_id) REFERENCES MLST(test_id)
);

CREATE TABLE MLST4_results (
    test_id         TEXT DEFAULT (lower(hex(randomblob(16)))),
    conv_nbr        INT NOT NULL,
    prev_msg        TEXT NOT NULL,
    testee_message  DOUBLE NOT NULL,
    pos_pred        DOUBLE NOT NULL,
    neg_pred        DOUBLE NOT NULL,
    FOREIGN KEY     (test_id) REFERENCES MLST(test_id)
);

CREATE TABLE MLST2_word_counter (
    test_id         TEXT DEFAULT (lower(hex(randomblob(16)))),
    conv_nbr        INT NOT NULL,
    word            TEXT NOT NULL,
    frequency       INT NOT NULL,
    FOREIGN KEY     (test_id) REFERENCES MLST(test_id)
);

CREATE TABLE MLST2_frequency_list (
    test_id         TEXT DEFAULT (lower(hex(randomblob(16)))),
    conv_nbr        INT NOT NULL,
    word_rank       INT NOT NULL,
    frequency       INT NOT NULL,
    FOREIGN KEY     (test_id) REFERENCES MLST(test_id)
);

CREATE TABLE MLST2_non_frequent_list (
    test_id         TEXT DEFAULT (lower(hex(randomblob(16)))),
    conv_nbr        INT NOT NULL,
    word            TEXT NOT NULL,
    frequency       INT NOT NULL,
    FOREIGN KEY     (test_id) REFERENCES MLST(test_id)
);

CREATE TABLE MLST2TC2_results (
    test_id             TEXT DEFAULT (lower(hex(randomblob(16)))),
    conv_nbr            INT NOT NULL,
    amount_sents        INT NOT NULL,
    amount_words        INT NOT NULL,
    amount_words_grt_6  INT NOT NULL,
    readab_index        DOUBLE NOT NULL,
    FOREIGN KEY         (test_id) REFERENCES MLST(test_id)
);


/* INSERT 
INTO GDMs(gdm_id)
VALUES ('Aida'),
        ('Emely');

INSERT
INTO MLST7(test_id, gdm_id, date_time_run)
VALUES ('1', 'Aida', '2022-04-05 12:58:10'),
        ('2', 'Emely', '2022-04-05 12:58:11');

INSERT
INTO MLST7_results(test_id, conv_nbr, toxicity_type, toxicity_level)
VALUES ('1', 1, 'Toxicity', 0.5),
        ('1', 2, 'Toxicity', 0.3),
        ('2', 1, 'Toxicity', 0.8),
        ('2', 2, 'Toxicity', 0.9); */