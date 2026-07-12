param(
    [string]$DbPath = ".\data\todo_demo.db",
    [string]$SummaryCsvPath = ".\output\reports\summary_metrics.csv",
    [double]$AvgTolerance = 0.01
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $DbPath)) {
    throw "Database file not found: $DbPath"
}

if (-not (Test-Path $SummaryCsvPath)) {
    throw "Summary CSV file not found: $SummaryCsvPath"
}

$csv = Import-Csv $SummaryCsvPath

function Get-MetricValue {
    param(
        [string]$Name
    )

    $value = ($csv | Where-Object { $_.metric -eq $Name }).value

    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Metric '$Name' not found in $SummaryCsvPath"
    }

    return $value
}

$sqlCompletionRaw = sqlite3 $DbPath "SELECT ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) FROM todos;"
$sqlOverdueRaw = sqlite3 $DbPath "SELECT COUNT(*) FROM todos WHERE due_date IS NOT NULL AND date(due_date) < date('now') AND status != 'completed';"
$sqlAvgCompletionRaw = sqlite3 $DbPath "SELECT ROUND(AVG(julianday(completed_at) - julianday(created_at)), 2) FROM todos WHERE status = 'completed' AND completed_at IS NOT NULL;"

$csvCompletion = [decimal](Get-MetricValue "completion_rate_pct")
$csvOverdue = [int](Get-MetricValue "overdue_tasks")
$csvAvgCompletion = [decimal](Get-MetricValue "avg_completion_days")

$sqlCompletion = [decimal]$sqlCompletionRaw
$sqlOverdue = [int]$sqlOverdueRaw
$sqlAvgCompletion = [decimal]$sqlAvgCompletionRaw

$errors = @()

if ($csvCompletion -ne $sqlCompletion) {
    $errors += "completion_rate_pct mismatch: CSV=$csvCompletion SQL=$sqlCompletion"
}

if ($csvOverdue -ne $sqlOverdue) {
    $errors += "overdue_tasks mismatch: CSV=$csvOverdue SQL=$sqlOverdue"
}

if ([math]::Abs([double]$csvAvgCompletion - [double]$sqlAvgCompletion) -gt $AvgTolerance) {
    $errors += "avg_completion_days mismatch: CSV=$csvAvgCompletion SQL=$sqlAvgCompletion tolerance=$AvgTolerance"
}

if ($errors.Count -eq 0) {
    Write-Host "All analytics checks passed ✅" -ForegroundColor Green
    Write-Host "completion_rate_pct = $csvCompletion"
    Write-Host "overdue_tasks = $csvOverdue"
    Write-Host "avg_completion_days = $csvAvgCompletion"
    exit 0
}

$errors | ForEach-Object {
    Write-Host $_ -ForegroundColor Red
}

throw "Analytics validation failed."