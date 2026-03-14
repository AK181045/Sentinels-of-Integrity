import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PROJECT_DIR = r"c:\Users\SAI\Desktop\Sentinals of integrity"

class AutoSyncHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.last_sync = time.time()
        self.cooldown = 10  # Seconds to wait before syncing again to batch events

    def sync_to_github(self):
        print(f"\n[🔄] Change detected! Auto-syncing to GitHub...")
        try:
            # Add all new changes
            subprocess.run(['git', 'add', '.'], cwd=PROJECT_DIR, check=True, capture_output=True)
            
            # Use porcelain to check if there are actual commit-able files
            status = subprocess.run(['git', 'status', '--porcelain'], cwd=PROJECT_DIR, capture_output=True, text=True)
            if not status.stdout.strip():
                return # No files actually modified
                
            # Commit and push
            commit_msg = f"Auto-sync update - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=PROJECT_DIR, check=True)
            
            # Using push without tracking to avoid some silent failures
            push = subprocess.run(['git', 'push', 'origin', 'main'], cwd=PROJECT_DIR, capture_output=True, text=True)
            
            if push.returncode == 0:
                print(f"[✅] Successfully automatically synced to GitHub!")
            else:
                print(f"[⚠️] Push failed: {push.stderr}")
                
        except Exception as e:
            print(f"[❌] Sync failed: {e}")

    def on_any_event(self, event):
        # Ignore .git folder changes to prevent infinite loops
        if '.git' in event.src_path or '__pycache__' in event.src_path:
            return
            
        current_time = time.time()
        if (current_time - self.last_sync) > self.cooldown:
            self.last_sync = current_time
            self.sync_to_github()

if __name__ == "__main__":
    print(f"==================================================")
    print(f"   Sentinels of Integrity | Background Autosync   ")
    print(f"   Monitoring folder: {PROJECT_DIR}               ")
    print(f"   Every time you edit a file, it will instantly  ")
    print(f"   be uploaded to your GitHub!                    ")
    print(f"==================================================")
    
    event_handler = AutoSyncHandler()
    observer = Observer()
    observer.schedule(event_handler, PROJECT_DIR, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
