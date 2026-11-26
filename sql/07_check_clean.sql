-- 1. Rows kept vs raw
SELECT (SELECT COUNT(*) FROM raw_reviews_v2) AS raw_rows,
       (SELECT COUNT(*) FROM clean_reviews)  AS clean_rows;

-- 2. Short reviews by rating group
SELECT rating_group,
       COUNT(*) AS reviews,
       COUNT(*) FILTER (WHERE is_short) AS short_reviews
FROM clean_reviews
GROUP BY rating_group
ORDER BY rating_group;

-- 3. Negative reviews per app and month (time coverage)
SELECT app, review_month, COUNT(*) AS negative_reviews
FROM clean_reviews
WHERE rating_group = 'negative'
GROUP BY app, review_month
ORDER BY app, review_month;

-- 4. App version coverage among negative reviews
SELECT app,
       COUNT(*) AS negative_reviews,
       COUNT(*) FILTER (WHERE app_version IS NOT NULL) AS with_version
FROM clean_reviews
WHERE rating_group = 'negative'
GROUP BY app;
