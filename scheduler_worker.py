import time
import signal
import sys
from scheduler import start_scheduler

def graceful_shutdown(signum, frame):
    print("\n Scheduler shutting down...")
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)

if __name__ == "__main__":
    print(" Starting Outreach Scheduler Worker...")
    scheduler = start_scheduler()
    
    # Keep worker alive indefinitely
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print(" Scheduler stopped.")