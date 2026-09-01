import os
import pandas as pd

def generate_demo_data():
    os.makedirs("data/demo", exist_ok=True)
    
    # 1. FIR Data (Text)
    fir_1 = "Rahul Sharma met Amit Verma near Bhopal railway station. Ravi Kumar was also mentioned in the meeting. Rahul uses phone 9000000001."
    fir_2 = "Priya Singh was seen transferring packages to Vikram Gupta in Delhi. Mention of account belonging to Neha."
    fir_3 = "Suresh Patel is suspected of orchestrating the logistics. Rahul Sharma was seen at his warehouse."
    
    with open("data/demo/FIR_001.txt", "w") as f: f.write(fir_1)
    with open("data/demo/FIR_002.txt", "w") as f: f.write(fir_2)
    with open("data/demo/FIR_003.txt", "w") as f: f.write(fir_3)

    # 2. CDR Data (CSV)
    cdr_records = []
    for i in range(1, 6):
        cdr_records.append({"caller": "9000000001", "receiver": "9000000002", "date": f"2026-01-0{i}", "calls": 5})
    # Communication Spike
    cdr_records.append({"caller": "9000000001", "receiver": "9000000002", "date": "2026-01-15", "calls": 78})
    # Bridge connection 
    cdr_records.append({"caller": "9000000009", "receiver": "9000000001", "date": "2026-01-10", "calls": 12})
    cdr_records.append({"caller": "9000000009", "receiver": "9000000088", "date": "2026-01-11", "calls": 15})
    
    pd.DataFrame(cdr_records).to_csv("data/demo/cdr.csv", index=False)

    # 3. Financial Data (CSV) 
    fin_records = [
        {"transaction_id": "TX001", "sender": "Amit Verma", "receiver": "Rahul Sharma", "amount": 80000, "date": "2026-01-14"},
        {"transaction_id": "TX002", "sender": "Rahul Sharma", "receiver": "Ravi Kumar", "amount": 70000, "date": "2026-01-15"},
        {"transaction_id": "TX003", "sender": "Ravi Kumar", "receiver": "Amit Verma", "amount": 60000, "date": "2026-01-16"}, 
        {"transaction_id": "TX004", "sender": "Priya Singh", "receiver": "Vikram Gupta", "amount": 50000, "date": "2026-01-17"} 
    ]
    pd.DataFrame(fin_records).to_csv("data/demo/transactions.csv", index=False)
