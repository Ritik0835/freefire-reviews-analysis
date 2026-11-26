-- 1. Rows, distinct IDs and date range per app and country
SELECT app, country,
       COUNT(*) AS total_rows,
       COUNT(DISTINCT review_id) AS distinct_ids,
       MIN(reviewed_at)::date AS first_review,
       MAX(reviewed_at)::date AS last_review
FROM raw_reviews
GROUP BY app, country
ORDER BY app, country;

-- 2. How many countries does each review ID appear in?
SELECT countries_per_id, COUNT(*) AS review_ids
FROM (
    SELECT review_id, COUNT(DISTINCT country) AS countries_per_id
    FROM raw_reviews
    GROUP BY review_id
) t
GROUP BY countries_per_id
ORDER BY countries_per_id;

-- 3. Which country pairs share reviews?
SELECT a.country AS country_1, b.country AS country_2, COUNT(*) AS shared_reviews
FROM (SELECT DISTINCT review_id, country FROM raw_reviews) a
JOIN (SELECT DISTINCT review_id, country FROM raw_reviews) b
  ON a.review_id = b.review_id AND a.country < b.country
GROUP BY a.country, b.country
ORDER BY shared_reviews DESC;
