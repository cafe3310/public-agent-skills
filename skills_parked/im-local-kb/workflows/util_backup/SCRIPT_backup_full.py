import os
import zipfile
import datetime
import argparse
import sys

def backup_workspace(source_dir, backup_dir):
    """
    Backs up the entire workspace to a timestamped zip file.
    
    Args:
        source_dir (str): The root directory to backup (e.g., 'kb').
        backup_dir (str): The directory to store the backup zip files (e.g., 'kb/backups').
    """
    # Ensure source directory exists
    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        sys.exit(1)

    # Ensure backup directory exists
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Generate timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{timestamp}.zip"
    backup_path = os.path.join(backup_dir, backup_filename)

    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                # Exclude the backup directory itself to avoid recursion
                # resolve relative paths to absolute to compare correctly
                abs_root = os.path.abspath(root)
                abs_backup_dir = os.path.abspath(backup_dir)
                
                if abs_root.startswith(abs_backup_dir):
                    continue

                for file in files:
                    file_path = os.path.join(root, file)
                    # Create relative path for archive
                    arcname = os.path.relpath(file_path, start=source_dir)
                    zipf.write(file_path, arcname)
        
        print(f"[SUCCESS] Backup created at: {backup_path}")
        
        # Optional: Rotation logic (keep last 5 backups)
        # list all zip files in backup_dir starting with "backup_"
        backups = [
            os.path.join(backup_dir, f) 
            for f in os.listdir(backup_dir) 
            if f.startswith("backup_") and f.endswith(".zip")
        ]
        backups.sort(key=os.path.getmtime)
        
        # Keep last 5
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                os.remove(old_backup)
                print(f"[INFO] Removed old backup: {old_backup}")

    except Exception as e:
        print(f"[ERROR] Backup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup the KB workspace.")
    parser.add_argument("--source", default="kb", help="Source directory to backup")
    parser.add_argument("--dest", default="kb/backups", help="Destination directory for backups")
    
    args = parser.parse_args()
    
    backup_workspace(args.source, args.dest)
