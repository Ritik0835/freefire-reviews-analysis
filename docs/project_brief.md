# Project Brief: Free Fire Player Dissatisfaction Analysis

## Business Question
What drives player dissatisfaction in Free Fire, and what should the product team fix first?

## Stakeholder
A Free Fire product manager who needs to decide which player complaints to prioritize in the next update cycle.

## Success Metric
- Goal: improve the average Google Play star rating
- Measured by: share of negative reviews (1-2 stars) per complaint category, and how much each category lowers the average rating

## Sub-Questions
1. What are the most common complaint categories (lag, hackers, matchmaking, payments, updates, device issues)?
2. Which complaint category lowers ratings the most?
3. Do complaints spike after specific app versions or updates?
4. How do Free Fire and Free Fire MAX compare?
5. How do complaints differ between India and other countries?

## Data Source
Google Play reviews scraped with the `google-play-scraper` Python library for Free Fire (`com.dts.freefireth`) and Free Fire MAX (`com.dts.freefiremax`), across multiple countries (India, Brazil, Indonesia, US). Fields: review text, rating, date, app version, thumbs-up count, developer reply.

## Known Limits
- Scraped public reviews only, so there is selection bias (unhappy players write more reviews).
- Free Fire is banned in India, so Indian reviews mostly come from Free Fire MAX.
- Reviews are in mixed languages (including Hinglish), so keyword-based categorizing will be imperfect. I will validate accuracy on a manually labelled sample.
