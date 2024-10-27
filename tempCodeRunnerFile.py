import os
import hashlib
import shutil
import re
import sys


def hash_file(file_path):
    """Return the SHA-1 hash of the file in chunks to handle large files efficiently."""
    hasher = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):  # Read in chunks of 8KB
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicates(folder_path):
    """Find and move duplicate files in the given folder."""
    hashes = {}
    duplicates_folder = os.path.join(folder_path, 'duplicates')
    originals_folder = os.path.join(folder_path, 'originals')
    os.makedirs(duplicates_folder, exist_ok=True)
    os.makedirs(originals_folder, exist_ok=True)
    duplicate_count = 0  # Counter for moved duplicates

    for root, dirs, files in os.walk(folder_path):
        if duplicates_folder in root or originals_folder in root:  # Skip these folders to avoid re-processing
            continue

        for file in files:
            file_path = os.path.join(root, file)
            file_hash = hash_file(file_path)
            file_base_name = re.sub(r' copy.*', '', os.path.splitext(file)[0])

            if file_hash in hashes:
                # Move the duplicate file to the duplicates folder
                file_folder = os.path.join(duplicates_folder, file_base_name)
                os.makedirs(file_folder, exist_ok=True)
                try:
                    shutil.move(file_path, os.path.join(file_folder, file))
                    print(f"Moved duplicate: {file_path} to {file_folder}")
                    duplicate_count += 1
                except Exception as e:
                    print(f"Error moving duplicate {file_path}: {e}")
            else:
                # Move the original file to the originals folder
                original_file_folder = os.path.join(
                    originals_folder, file_base_name)
                os.makedirs(original_file_folder, exist_ok=True)
                try:
                    shutil.move(file_path, os.path.join(
                        original_file_folder, file))
                    print(f"Moved original: {file_path} to {
                          original_file_folder}")
                    hashes[file_hash] = {'path': os.path.join(
                        original_file_folder, file), 'moved': True}
                except Exception as e:
                    print(f"Error moving original {file_path}: {e}")

    print(f"\nTotal duplicates moved: {duplicate_count}")


if __name__ == "__main__":
    downloads_folder = os.path.expanduser('~/Nedlastinger')
    if not os.path.isdir(downloads_folder):
        downloads_folder = os.path.expanduser('~/Downloads')

    if not os.path.isdir(downloads_folder):
        print(f"The specified path {downloads_folder} is not a directory.")
        sys.exit(1)

    find_duplicates(downloads_folder)
