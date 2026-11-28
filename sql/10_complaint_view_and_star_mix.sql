-- One row per (review, complaint category). Reviews with no category have no rows.
DROP VIEW IF EXISTS complaint_long;

CREATE VIEW complaint_long AS
SELECT review_id, app, language, score, rating_group, review_date, review_month, app_version, has_reply, 'lag_performance' AS category
FROM review_categories WHERE lag_performance
UNION ALL
SELECT review_id, app, language, score, rating_group, review_date, review_month, app_version, has_reply, 'server_connection' AS category
FROM review_categories WHERE server_connection
UNION ALL
SELECT review_id, app, language, score, rating_group, review_date, review_month, app_version, has_reply, 'download_open_crash' AS category
FROM review_categories WHERE download_open_crash
UNION ALL
SELECT review_id, app, language, score, rating_group, review_date, review_month, app_version, has_reply, 'hackers_cheaters' AS category
FROM review_categories WHERE hackers_cheaters
UNION ALL
SELECT review_id, app, language, score, rating_group, review_date, review_month, app_version, has_reply, 'pricing_pay2win' AS category
FROM review_categories WHERE pricing_pay2win
UNION ALL
SELECT review_id, app, language, score, rating_group, review_date, review_month, app_version, has_reply, 'payment_missing_items' AS category
FROM review_categories WHERE payment_missing_items
UNION ALL
SELECT review_id, app, language, score, rating_group, review_date, review_month, app_version, has_reply, 'matchmaking_balance' AS category
FROM review_categories WHERE matchmaking_balance
UNION ALL
SELECT review_id, app, language, score, rating_group, review_date, review_month, app_version, has_reply, 'bugs_glitches' AS category
FROM review_categories WHERE bugs_glitches
UNION ALL
SELECT review_id, app, language, score, rating_group, review_date, review_month, app_version, has_reply, 'account_ban_loss' AS category
FROM review_categories WHERE account_ban_loss
UNION ALL
SELECT review_id, app, language, score, rating_group, review_date, review_month, app_version, has_reply, 'content_events_changes' AS category
FROM review_categories WHERE content_events_changes
UNION ALL
SELECT review_id, app, language, score, rating_group, review_date, review_month, app_version, has_reply, 'device_optimization' AS category
FROM review_categories WHERE device_optimization
UNION ALL
SELECT review_id, app, language, score, rating_group, review_date, review_month, app_version, has_reply, 'general_negative' AS category
FROM review_categories WHERE general_negative;


-- Complaint mix in 1-star vs 2-star reviews
WITH totals AS (
    SELECT COUNT(*) FILTER (WHERE score = 1) AS n1,
           COUNT(*) FILTER (WHERE score = 2) AS n2
    FROM review_categories
    WHERE score IN (1, 2)
),
cat AS (
    SELECT category,
           COUNT(*) FILTER (WHERE score = 1) AS flagged_1star,
           COUNT(*) FILTER (WHERE score = 2) AS flagged_2star
    FROM complaint_long
    WHERE score IN (1, 2)
    GROUP BY category
)
SELECT cat.category,
       cat.flagged_1star,
       cat.flagged_2star,
       ROUND(100.0 * cat.flagged_1star / totals.n1, 1) AS pct_of_1star_reviews,
       ROUND(100.0 * cat.flagged_2star / totals.n2, 1) AS pct_of_2star_reviews,
       ROUND((1.0 * cat.flagged_1star / totals.n1)
             / NULLIF(1.0 * cat.flagged_2star / totals.n2, 0), 2) AS ratio_1star_vs_2star,
       RANK() OVER (ORDER BY cat.flagged_1star DESC) AS rank_by_1star_volume
FROM cat CROSS JOIN totals
ORDER BY ratio_1star_vs_2star DESC;
