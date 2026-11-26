DROP TABLE IF EXISTS raw_reviews;

CREATE TABLE raw_reviews (
    review_id               TEXT,
    user_name               TEXT,
    user_image              TEXT,
    content                 TEXT,
    score                   INT,
    thumbs_up_count         INT,
    review_created_version  TEXT,
    reviewed_at             TIMESTAMP,
    reply_content           TEXT,
    replied_at              TIMESTAMP,
    app_version             TEXT,
    app                     TEXT,
    country                 TEXT,
    lang_requested          TEXT
);
