import os
import hashlib
import argparse
import shutil
import time

def get_file_hash(file_path, hash_algo=hashlib.sha256):
    """Calculate the hash of a file."""
    hash_obj = hash_algo()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def generate_file_identifier(file_path):
    """Generate a unique identifier for a file."""
    file_size = os.path.getsize(file_path)
    file_hash = get_file_hash(file_path, hashlib.sha256)
    return f"{file_size}_{file_hash}"

def find_duplicates(directories):
    """Find duplicate files in the given directories."""
    file_dict = {}

    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_id = generate_file_identifier(file_path)
                file_info = {
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'type': os.path.splitext(file_path)[1],
                    'modified_time': os.path.getmtime(file_path)
                }

                if file_id in file_dict:
                    file_dict[file_id].append(file_info)
                else:
                    file_dict[file_id] = [file_info]
    # Filter out file_ids with only one element
    file_dict = {file_id: file_info_list for file_id, file_info_list in file_dict.items() if len(file_info_list) >= 2}

    return file_dict

def assign_priorities(file_dict, keyword, priority_order=None):
    """Assign priorities to files based on the given criteria."""
    if priority_order is None:
        # Default priority order: size, directory depth, modified time
        priority_order = ['size', 'path', 'modified_time']


    for file_id, files in file_dict.items():
        priority_counter = 1  # Start from 1 for non-keyword files
        if keyword:
            keyword_files = [file for file in files if keyword in file['path']]
            non_keyword_files = [file for file in files if keyword not in file['path']]

            # Assign priority 0 to files containing the keyword
            for file_info in keyword_files:
                file_info['priority'] = 0

            # Sort non-keyword files by the custom priority order
            non_keyword_files.sort(
                key=lambda x: tuple(-x[order] if order != 'path' else -x[order].count(os.sep) for order in priority_order)
            )

            # Assign priorities to non-keyword files
            for file_info in non_keyword_files:
                file_info['priority'] = priority_counter
                priority_counter += 1
        else:
            # If keyword is empty, sort all files by the custom priority order
            files.sort(
                key=lambda x: tuple(-x[order] if order != 'path' else -x[order].count(os.sep) for order in priority_order)
            )

            # Assign priorities to all files
            for file_info in files:
                file_info['priority'] = priority_counter
                priority_counter += 1

def retain_files(file_dict, action, move_to_dir=None, try_run=False):
    """Retain files based on the priority and process the rest."""
    files_to_process = []
    files_to_retain = []

    for file_id, files in file_dict.items():
        # Retain files with priority 0
        retained_files = [file for file in files if file['priority'] == 0]
        non_zero_priority_files = [file for file in files if file['priority'] != 0]

        # If there are non-zero priority files, retain the one with the highest priority (lowest priority number)
        if non_zero_priority_files:
            best_file = min(non_zero_priority_files, key=lambda x: x['priority'])
            retained_files.append(best_file)
            files_to_process.extend([file for file in non_zero_priority_files if file != best_file])
        files_to_retain.extend(retained_files)
    process_files(files_to_process, action, move_to_dir, try_run)

def process_files(files, action, move_to_dir=None, try_run=False):
    if action == 'delete':
        for file in files:
            if try_run:
                print(f"Would delete: {file['path']}")
            else:
                try:
                    os.remove(file['path'])
                    print(f"Deleted: {file['path']}")
                except Exception as e:
                    print(f"Error deleting {file['path']}: {e}")
    elif action == 'move':
        if move_to_dir:
            if not os.path.exists(move_to_dir):
                os.makedirs(move_to_dir)
            for file in files:
                if try_run:
                    file_name = file['path'].replace('/', '___')
                    new_path = os.path.join(move_to_dir, file_name)
                    print(f"Would move: {file['path']} to {new_path}")
                else:
                    try:
                        file_name = file['path'].replace('/', '___')
                        new_path = os.path.join(move_to_dir, file_name)
                        shutil.move(file['path'], new_path)
                        print(f"Moved: {file['path']} to {new_path}")
                    except Exception as e:
                        print(f"Error moving {file['path']} to {move_to_dir}: {e}")
        else:
            for file in files:
                if try_run:
                    new_path = file['path'] + '.dup_finder'
                    print(f"Would rename: {file['path']} to {new_path}")
                else:
                    try:
                        new_path = file['path'] + '.dup_finder'
                        shutil.move(file['path'], new_path)
                        print(f"Renamed: {file['path']} to {new_path}")
                    except Exception as e:
                        print(f"Error renaming {file['path']} to {new_path}: {e}")

def main(directories, keyword, action, priority_order=None, move_to_dir=None, try_run=False):
    file_dict = find_duplicates(directories)
    assign_priorities(file_dict, keyword, priority_order)
    retain_files(file_dict, action, move_to_dir, try_run)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find and process duplicate files.")
    parser.add_argument("directories", nargs='+', help="Directories to search for duplicate files")
    parser.add_argument("--keyword", required=False, help="Keyword to retain files")
    parser.add_argument("--action", choices=['delete', 'move'], required=False, default='move', help="Action to process files (default: move)")
    parser.add_argument("--priority-order", nargs='+', required=False, help="Custom priority order: size, path, modified_time")
    parser.add_argument("--move-to-dir", required=False, help="Directory to move files to (if not specified, rename files with .dup_finder suffix)")
    parser.add_argument("--try-run", "-n", action='store_true', required=False, help="Try run mode: only print actions without executing them")

    args = parser.parse_args()

    main(args.directories, args.keyword, args.action, args.priority_order, args.move_to_dir, args.try_run)
