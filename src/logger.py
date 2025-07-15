from datetime import datetime
import csv
import os

LOG_FILE = "logs/expression_log.csv"

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

if not os.path.isfile(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
    with open(LOG_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "face_id", "expression"])

face_counter = 0

def log_expression(expressions):
    global face_counter
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        for expr in expressions:
            writer.writerow([timestamp, face_counter, expr])
            face_counter += 1
