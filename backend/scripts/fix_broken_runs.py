
import sqlite3
import json
import os

DB_PATH = "data/local_app.db"

def fix_runs():
    print(f"Connecting to {DB_PATH} using absolute path {os.path.abspath(DB_PATH)}...")
    if not os.path.exists(DB_PATH):
        print("DB DOES NOT EXIST!")
        return

    try:
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        # DEBUG: Print count of all runs
        cur.execute("SELECT count(*) as c FROM runs")
        print(f"Total runs in DB: {cur.fetchone()['c']}")

        cur.execute("SELECT id, steps_json, status FROM runs")
        rows = cur.fetchall()
        
        fixed_count = 0
        
        for row in rows:
            run_id = row['id']
            status = row['status']
            raw_steps = row['steps_json']
            
            if not raw_steps:
                continue
            
            try:
                steps = json.loads(raw_steps)
            except:
                continue

            modified = False
            
            # Condition 1: Status is error/failed/validation_failed
            if status in ('error', 'failed', 'validation_failed'):
                for step, step_status in steps.items():
                    if step_status == 'running':
                        print(f"Run {run_id} ({status}): Found stuck step '{step}'")
                        steps[step] = 'failed'
                        modified = True
                    elif step_status == 'pending':
                         # Optional: User said convert pending -> skipped
                        steps[step] = 'skipped'
                        modified = True
            
            # Condition 2: Status is Running (Zombie)
            if status == 'running':
                 # Check if it's actually running?
                 # We'll just be safe and assume if steps are stuck running and we are running this script, we want to kill them?
                 # No, user script logic was specific.
                 pass

            if modified:
                print(f"Fixing run {run_id}...")
                cur.execute("UPDATE runs SET steps_json = ? WHERE id = ?", (json.dumps(steps), run_id))
                fixed_count += 1
                
        con.commit()
        print(f"Fixed {fixed_count} runs.")
        con.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_runs()
