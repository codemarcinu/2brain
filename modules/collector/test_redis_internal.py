
from shared.messaging import TaskQueue
import sys

try:
    q = TaskQueue()
    res = q.send_to_refinery({"id": "test_manual", "data": "test_data"})
    print(f"Result: {res}")
except Exception as e:
    print(f"Error: {e}")
