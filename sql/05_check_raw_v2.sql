-- 1. Rows, distinct IDs and date range per app and language
SELECT app, language,
       COUNT(*) AS total_rows,
       COUNT(DISTINCT review_id) AS distinct_ids,
       MIN(reviewed_at)::date AS first_review,
       MAX(reviewed_at)::date AS last_review
FROM raw_reviews_v2
GROUP BY app, language
ORDER BY app, language;

-- 2. Star distribution per app
SELECT app, score, COUNT(*) AS reviews
FROM raw_reviews_v2
GROUP BY app, score
ORDER BY app, score;

-- 3. Overall duplicate check
SELECT COUNT(*) AS total_rows,
       COUNT(DISTINCT review_id) AS distinct_ids
FROM raw_reviews_v2;

-- 4. Missing versions and developer replies
SELECT COUNT(*) FILTER (WHERE app_version IS NULL) AS no_version,
       COUNT(*) FILTER (WHERE reply_content IS NOT NULL) AS with_reply
FROM raw_reviews_v2;

