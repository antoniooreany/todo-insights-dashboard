-- 1. Tasks created by day
SELECT
    date(created_at) AS created_day,
    COUNT(*) AS tasks_created
FROM todos
GROUP BY date(created_at)
ORDER BY created_day;

-- 2. Tasks created by week
SELECT
    strftime('%Y-%W', created_at) AS created_week,
    COUNT(*) AS tasks_created
FROM todos
GROUP BY strftime('%Y-%W', created_at)
ORDER BY created_week;

-- 3. Overall completion rate
SELECT
    COUNT(*) AS total_tasks,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS completion_rate_pct
FROM todos;

-- 4. Overdue task count
SELECT
    COUNT(*) AS overdue_tasks
FROM todos
WHERE due_date IS NOT NULL
  AND date(due_date) < date('now')
  AND status != 'completed';

-- 5. Average completion time in days
SELECT
    ROUND(AVG(julianday(completed_at) - julianday(created_at)), 2) AS avg_completion_days
FROM todos
WHERE status = 'completed'
  AND completed_at IS NOT NULL;

-- 6. Open tasks by category
SELECT
    category,
    COUNT(*) AS open_tasks
FROM todos
WHERE status != 'completed'
GROUP BY category
ORDER BY open_tasks DESC, category;