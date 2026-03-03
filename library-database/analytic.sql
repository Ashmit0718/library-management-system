-- Find Trending Books (Most borrowed in the last 30 days)
SELECT b.id, b.title, b.author, b.genre, COUNT(br.id) AS borrow_count
FROM books b
JOIN borrow_records br ON br.book_id = b.id
WHERE br.borrowed_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY b.id
ORDER BY borrow_count DESC
LIMIT 10;

-- Top 20 Member Leaderboard
SELECT u.id, u.name,
       COUNT(br.id) AS total_borrows,
       SUM(br.status = 'returned') AS returned,
       SUM(br.status = 'overdue') AS overdue,
       RANK() OVER (ORDER BY COUNT(br.id) DESC) AS rank_pos
FROM users u
LEFT JOIN borrow_records br ON br.user_id = u.id
WHERE u.role = 'member' AND u.is_active = 1
GROUP BY u.id
ORDER BY rank_pos
LIMIT 20;

-- Identify Overdue Books and Days Past Due
SELECT br.id, u.name AS user_name, u.email,
       b.title AS book_title,
       br.borrowed_at, br.due_date,
       DATEDIFF(NOW(), br.due_date) AS days_overdue
FROM borrow_records br
JOIN users u ON u.id = br.user_id
JOIN books b ON b.id = br.book_id
WHERE br.status = 'borrowed' AND br.due_date < NOW()
ORDER BY days_overdue DESC;