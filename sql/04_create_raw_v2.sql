DROP TABLE IF EXISTS raw_reviews_v2;

CREATE TABLE raw_reviews_v2 (
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
    language                TEXT
);
