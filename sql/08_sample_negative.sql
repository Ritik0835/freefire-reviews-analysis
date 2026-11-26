SELECT language, score, LEFT(content, 160) AS review_text
FROM (
    SELECT language, score, content,
           ROW_NUMBER() OVER (PARTITION BY language ORDER BY RANDOM()) AS rn
    FROM clean_reviews
    WHERE rating_group = 'negative'
      AND content_length >= 25
) t
WHERE rn <= 12
ORDER BY language, rn;
