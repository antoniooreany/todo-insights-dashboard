-- Total tasks
SELECT COUNT(*) AS total_tasks
FROM todos;

-- Open vs done
SELECT is_done, COUNT(*) AS task_count
FROM todos
GROUP BY is_done;

-- Completion rate
SELECT ROUND(100.0 * SUM(CASE WHEN is_done = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS completion_rate
FROM todos;

-- Overdue tasks
SELECT COUNT(*) AS overdue_tasks
FROM todos
WHERE is_done = 0
  AND due_date IS NOT NULL
  AND date(due_date) < date('now');

-- Average completion time in days
SELECT ROUND(AVG(julianday(completed_at) - julianday(created_at)), 2) AS avg_completion_days
FROM todos
WHERE completed_at IS NOT NULL;

-- Tasks created over time
SELECT date(created_at) AS created_day, COUNT(*) AS created_count
FROM todos
GROUP BY date(created_at)
ORDER BY created_day;

-- Tasks completed over time
SELECT date(completed_at) AS completed_day, COUNT(*) AS completed_count
FROM todos
WHERE completed_at IS NOT NULL
GROUP BY date(completed_at)
ORDER BY completed_day;

-- Tasks by category
SELECT category, COUNT(*) AS task_count
FROM todos
GROUP BY category
ORDER BY task_count DESC;
