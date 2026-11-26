DROP TABLE IF EXISTS clean_reviews;

CREATE TABLE clean_reviews AS
WITH base AS (
    SELECT
        review_id,
        app,
        language,
        score,
        CASE WHEN score <= 2 THEN 'negative'
             WHEN score = 3  THEN 'neutral'
             ELSE 'positive' END AS rating_group,
        TRIM(REGEXP_REPLACE(content, '\s+', ' ', 'g')) AS content,
        thumbs_up_count,
        reviewed_at,
        reviewed_at::date AS review_date,
        DATE_TRUNC('month', reviewed_at)::date AS review_month,
        COALESCE(app_version, review_created_version) AS app_version,
        reply_content,
        replied_at,
        (reply_content IS NOT NULL) AS has_reply
    FROM raw_reviews_v2
    WHERE content IS NOT NULL
      AND TRIM(content) <> ''
)
SELECT
    *,
    LENGTH(content) AS content_length,
    (LENGTH(content) < 10) AS is_short,
    COUNT(*) OVER (PARTITION BY app, LOWER(content)) AS same_text_count
FROM base;
