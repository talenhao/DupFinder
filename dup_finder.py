import os
import sys
import json
import shutil
import hashlib
import tempfile
import argparse
import subprocess
import datetime
from filelock import FileLock
from logger import configure_logger


logger = configure_logger("DupFinder")


def get_file_hash(file_path, hash_algo=hashlib.sha256):
    """Calculate the hash of a file."""
    hash_obj = hash_algo()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def generate_file_identifier(file_path):
    """Generate a unique identifier for a file."""
    file_hash = get_file_hash(file_path, hashlib.sha256)
    return file_hash

def write_cache_to_file(cache, cache_file):
    """Write the cache to the cache file atomically."""
    with tempfile.NamedTemporaryFile('w', delete=False) as temp_file:
        json.dump(cache, temp_file)
        temp_file_path = temp_file.name
    shutil.move(temp_file_path, cache_file)

def load_cache(cache_file):
    """Load the cache from the cache file."""
    if not os.path.exists(cache_file):
        return {}
    try:
        with open(cache_file, 'r') as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        os.remove(cache_file)
        return {}

def update_cache(cache, file_path, file_id):
    """Update the cache with the file information."""
    cache[file_path] = {
        'file_id': file_id,
        'modified_time': os.path.getmtime(file_path),
        'size': os.path.getsize(file_path)
    }

def get_file_id(file_path, cache):
    """Process a single file and return its file ID."""
    file_info = cache.get(file_path)
    if file_info:
        cached_modified_time = file_info.get('modified_time')
        cached_size = file_info.get('size')
        current_modified_time = os.path.getmtime(file_path)
        current_size = os.path.getsize(file_path)

        if cached_modified_time == current_modified_time and cached_size == current_size:
            return file_info['file_id']

    file_id = generate_file_identifier(file_path)
    update_cache(cache, file_path, file_id)
    return file_id
def find_duplicates(directories, cache_file='file_cache.json', batch_size=10):
    """Find duplicate files in the given directories."""
    lock_file = f"{cache_file}.lock"
    lock = FileLock(lock_file)

    with lock:
        cache = load_cache(cache_file)
        file_dict = {}
        cache_updates = []

        for directory in directories:
            logger.info("Processing directory: %s", directory)
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_id = get_file_id(file_path, cache)
                    if not file_id:
                        logger.error(f"Error generating file ID for {file_path}")
                        continue
                    file_info = {
                        'path': file_path,
                        'size': os.path.getsize(file_path),  # File size in bytes
                        'type': os.path.splitext(file_path)[1],
                        'modified_time': os.path.getmtime(file_path)
                    }
                    logger.debug("Process File ID: %s, File Info: %s", file_id, file_info)

                    if file_id in file_dict:
                        file_dict[file_id].append(file_info)
                    else:
                        file_dict[file_id] = [file_info]
                    # Track updated cache entries
                    cache_updates.append(file_path)
                    
                    # Write cache to file if batch size is reached
                    if len(cache_updates) >= batch_size:
                        write_cache_to_file(cache, cache_file)
                        cache_updates.clear()
                    
        # Final write for any remaining updates
        if cache_updates:
            write_cache_to_file(cache, cache_file)

        # Filter out file_ids with only one element
        file_dict = {file_id: file_info_list for file_id, file_info_list in file_dict.items() if len(file_info_list) >= 2}

    return file_dict

def parse_exclude_file(exclude_file):
    """Parse the exclude file and return a list of keywords."""
    try:
        with open(exclude_file, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        logger.error(f"Error reading exclude file {exclude_file}: {e}")
        return []

def assign_priorities(file_dict, exclude_keywords, exclude_file, priority_order=None):
    """Assign priorities to files based on the given criteria."""
    if priority_order is None:
        # Default priority order
        priority_order = ['modified_time', 'path']

    # Read exclude keywords from file if provided
    if exclude_file:
        exclude_keywords.extend(parse_exclude_file(exclude_file))

    for file_id, files in file_dict.items():
        # 检查同一 file_id 下的文件大小是否一致
        file_sizes = {file['size'] for file in files}
        if len(file_sizes) > 1:
            # 如果文件大小不一致，将所有文件的优先级设置为 0
            for file_info in files:
                file_info['priority'] = 0
            # 打印文件大小不一致的 file_id 及文件列表
            logger.error("File ID with inconsistent sizes: %s", file_id)
            for file_info in files:
                logger.warning(f"  Path: {file_info['path']}, Size: {file_info['size']}")
            continue

        priority_counter = 1  # Start from 1 for non-excluded files
        if exclude_keywords:
            excluded_files = [file for file in files if any(keyword in file['path'] for keyword in exclude_keywords)]
            non_excluded_files = [file for file in files if all(keyword not in file['path'] for keyword in exclude_keywords)]

            # Assign priority 0 to files containing any of the exclude keywords
            for file_info in excluded_files:
                file_info['priority'] = 0

            # Sort non-excluded files by the custom priority order
            non_excluded_files.sort(
                key=lambda x: tuple(-x[order] if order != 'path' else -x[order].count(os.sep) for order in priority_order)
            )

            # Assign priorities to non-excluded files
            for file_info in non_excluded_files:
                file_info['priority'] = priority_counter
                priority_counter += 1
        else:
            # If no exclude keywords, sort all files by the custom priority order
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
                logger.warning(f"Would delete: {file['path']}")
            else:
                try:
                    os.remove(file['path'])
                    logger.warning(f"Deleted: {file['path']}")
                except Exception as e:
                    logger.error(f"Error deleting {file['path']}: {e}")
    elif action == 'move':
        if move_to_dir:
            if not os.path.exists(move_to_dir):
                os.makedirs(move_to_dir)
            for file in files:
                if try_run:
                    file_name = file['path'].replace('/', '___')
                    new_path = os.path.join(move_to_dir, file_name)
                    logger.warning(f"Would move: {file['path']} to {new_path}")
                else:
                    try:
                        file_name = file['path'].replace('/', '___')
                        new_path = os.path.join(move_to_dir, file_name)
                        shutil.move(file['path'], new_path)
                        logger.warning(f"Moved: {file['path']} to {new_path}")
                    except Exception as e:
                        logger.error(f"Error moving {file['path']} to {move_to_dir}: {e}")
        else:
            for file in files:
                if try_run:
                    new_path = file['path'] + '.dup_finder'
                    logger.warning(f"Would rename: {file['path']} to {new_path}")
                else:
                    try:
                        new_path = file['path'] + '.dup_finder'
                        shutil.move(file['path'], new_path)
                        logger.warning(f"Renamed: {file['path']} to {new_path}")
                    except Exception as e:
                        logger.error(f"Error renaming {file['path']} to {new_path}: {e}")

def main(directories, exclude_keywords, exclude_file, action, priority_order=None, move_to_dir=None, try_run=False):
    file_dict = find_duplicates(directories)
    assign_priorities(file_dict, exclude_keywords, exclude_file, priority_order)
    # 保存 file_dict 到文件
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"duplicates_{current_time}.json"
    with open(output_file, 'w') as f:
        json.dump(file_dict, f, indent=4)
    logger.info(f"Saved file_dict to {output_file}")

    retain_files(file_dict, action, move_to_dir, try_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find and process duplicate files.")
    parser.add_argument("-d", "--directories", nargs='+', required=True, help="Directories to search for duplicate files")
    parser.add_argument("--exclude", nargs='+', required=False, help="Exclude keywords, ")
    parser.add_argument("--exclude-file", required=False, help="File containing exclude keywords, one per line")
    parser.add_argument("--action", choices=['delete', 'move'], required=False, default='move', help="Action to process files (default: move)")
    parser.add_argument("--priority-order", nargs='+', required=False, help="Custom priority order: default is modified_time, path")
    parser.add_argument("--move-to-dir", required=False, help="Directory to move files to (if not specified, rename files with .dup_finder suffix)")
    parser.add_argument("--try-run", "-n", action='store_true', required=False, help="Try run mode: only print actions without executing them")

    args = parser.parse_args()
    # 使用 subprocess.list2cmdline 重建命令行字符串
    command_line = subprocess.list2cmdline(sys.argv)
    logger.info("Full command line: %s", command_line)
    main(args.directories, args.exclude if args.exclude else [], args.exclude_file, args.action, args.priority_order, args.move_to_dir, args.try_run)
