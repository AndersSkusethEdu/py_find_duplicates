import os
import hashlib
import shutil


def hash_file(file_path):
    """Return the SHA-1 hash of the file."""
    hasher = hashlib.sha1()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def find_duplicates(folder_path):
    """Find and move duplicate files in the given folder."""
    hashes = {}
    duplicates_folder = os.path.join(folder_path, 'duplicates')
    os.makedirs(duplicates_folder, exist_ok=True)

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = hash_file(file_path)
            file_base_name = re.sub(r' copy.*', '', os.path.splitext(file)[0])

            if file_hash in hashes:
                original_path = hashes[file_hash]['path']

                # Create a folder named after the file base name
                file_folder = os.path.join(duplicates_folder, file_base_name)
                os.makedirs(file_folder, exist_ok=True)

                # Move the original file if not already moved
                if not hashes[file_hash]['moved']:
                    shutil.move(original_path, os.path.join(
                        file_folder, os.path.basename(original_path)))
                    hashes[file_hash]['moved'] = True

                # Move the duplicate file
                shutil.move(file_path, os.path.join(file_folder, file))
                print(f"Moved duplicate: {file_path} to {file_folder}")
            else:
                hashes[file_hash] = {'path': file_path, 'moved': False}


if __name__ == "__main__":
    downloads_folder = os.path.expanduser('~/Nedlastinger')
    if not os.path.isdir(downloads_folder):
        downloads_folder = os.path.expanduser('~/Downloads')

    if not os.path.isdir(downloads_folder):
        print(f"The specified path {downloads_folder} is not a directory.")
        sys.exit(1)

    find_duplicates(downloads_folder)
