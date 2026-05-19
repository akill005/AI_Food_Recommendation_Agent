import csv
import os
from datetime import datetime

CSV_FILE = "evaluation_metrics.csv"
def initialize_csv():

    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "query",
                "precision_at_5",
                "recall_at_5",
                "hit_rate",
                "latency",
                "results_count"
            ])

def log_metrics(
    query,
    precision,
    recall,
    hit_rate,
    latency,
    results_count
):

    initialize_csv()
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            query,
            precision,
            recall,
            hit_rate,
            latency,
            results_count
        ])