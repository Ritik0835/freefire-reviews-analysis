-- 1. Total rows and distinct review IDs (duplicates?)
SELECT COUNT(*) AS total_rows,
       COUNT(DISTINCT review_id) AS distinct_ids
FROM raw_reviews;

-- 2. Missing or very short review text
SELECT
  COUNT(*) FILTER (WHERE content IS NULL OR TRIM(content) = '') AS empty_text,
  COUNT(*) FILTER (WHERE LENGTH(TRIM(content)) < 5) AS under_5_chars
FROM raw_reviews;

-- 3. Date range per app
SELECT app, MIN(reviewed_at) AS first_review, MAX(reviewed_at) AS last_review
FROM raw_reviews
GROUP BY app;

-- 4. Rating distribution
SELECT score, COUNT(*) AS reviews
FROM raw_reviews
GROUP BY score
ORDER BY score;

-- 5. Missing app version
SELECT COUNT(*) FILTER (WHERE app_version IS NULL) AS no_version,
       COUNT(*) FILTER (WHERE reply_content IS NOT NULL) AS with_reply
FROM raw_reviews;

-- 6. Most repeated review texts (possible spam)
SELECT content, COUNT(*) AS times
FROM raw_reviews
GROUP BY content
HAVING COUNT(*) > 5
ORDER BY times DESC
LIMIT 10;
