import argparse, csv, os, sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
load_dotenv("backend/.env")
URL=os.getenv("DATABASE_URL","mysql+pymysql://root:change_me@localhost:3306/abandoned_cart_recovery")
# TABLES=["customers","consents","sessions","carts","cart_lines","campaigns","message_templates","send_attempts","orders","order_lines"]
TABLES = [
    "customers",
    "consents",
    "sessions",
    "carts",
    "cart_lines",
    "campaigns",
    "message_templates",
    "send_attempts",
    "orders",
    "order_lines",
    "attributions",
    "audit_decisions",
    "cart_events",
    "send_events",
    "anomaly_issues"
]

FILE_NAMES = {
    "anomaly_issues": "anomalies"
}

AUTO_ID_COLUMNS = {
    "attributions": "attribution_id",
    "audit_decisions": "decision_id",
    "cart_events": "event_id",
    "send_events": "event_id",
    "anomaly_issues": "issue_id"
}
def load(folder):
    engine=create_engine(URL, pool_pre_ping=True)
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        for table in TABLES:
            # path=Path(folder)/f"{table}.csv"
            file_name = FILE_NAMES.get(table, table)
            path = Path(folder) / f"{file_name}.csv"
            if not path.exists(): continue
            conn.execute(text(f"DELETE FROM {table}"))
            with path.open(encoding="utf-8",newline="") as f:
                rows=list(csv.DictReader(f))
            if rows:
                cols=list(rows[0].keys())
                # Generator's synthetic row IDs are translated to DB auto-increment IDs where needed.
                # if table in ("consents","cart_lines","order_lines"):
                #     for r in rows: r.pop(cols[0],None)
                #     cols=list(rows[0].keys())
                if table in ("consents", "cart_lines", "order_lines"):
                    for r in rows:
                        r.pop(cols[0], None)
                    cols = list(rows[0].keys())

                if table in AUTO_ID_COLUMNS:
                    id_column = AUTO_ID_COLUMNS[table]
                    for r in rows:
                        r.pop(id_column, None)
                    cols = list(rows[0].keys())
                stmt=text(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(':'+c for c in cols)})")
                for r in rows:
                    for k, v in list(r.items()):
                         if v == "":
                              r[k] = None
                         elif k in ("email_valid", "phone_valid"):
                              r[k] = 1 if v.lower() == "true" else 0
                    
                    conn.execute(stmt,r)
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    print(f"Loaded {folder} into MySQL.")
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--input",default="data/starter"); load(p.parse_args().input)
