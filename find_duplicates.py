import os
import hashlib
import shutil
import re
import sys


def hash_file(file_path):
    """Returnerer SHA-1 hash av filen, lest i deler for å håndtere store filer effektivt."""
    hasher = hashlib.sha1()
    with open(file_path, 'rb') as f:
        # Leser filen i biter på 8KB for å spare minnebruk
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicates(folder_path):
    """Finner og flytter duplikatfiler i den angitte mappen."""
    hashes = {}  # Ordbok for å lagre hash-verdier og filstier
    duplicates_folder = os.path.join(folder_path, 'duplicates')
    # Lager mappen for duplikater hvis den ikke finnes
    os.makedirs(duplicates_folder, exist_ok=True)
    duplicate_count = 0  # Teller for antall flyttede duplikater

    for root, dirs, files in os.walk(folder_path):
        # Hopp over duplikatmappen for å unngå å prosessere filer som allerede er flyttet
        if duplicates_folder in root:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            file_hash = hash_file(file_path)  # Genererer hash for filen
            # Fjerner "copy"-tekst fra filnavnet for å organisere filer etter originalen
            file_base_name = re.sub(r' copy.*', '', os.path.splitext(file)[0])

            if file_hash in hashes:
                # Hvis filen allerede er sett, definer som duplikat
                original_path = hashes[file_hash]['path']

                # Lager en undermappe i "duplicates" basert på filnavnet til originalen
                file_folder = os.path.join(duplicates_folder, file_base_name)
                os.makedirs(file_folder, exist_ok=True)

                # Flytter originalfilen hvis den ikke er flyttet tidligere
                if not hashes[file_hash]['moved']:
                    try:
                        shutil.move(original_path, os.path.join(
                            file_folder, os.path.basename(original_path)))
                        hashes[file_hash]['moved'] = True
                        duplicate_count += 1
                    except Exception as e:
                        print(f"Feil ved flytting av original {
                              original_path}: {e}")

                # Flytter duplikatfilen til samme undermappe
                try:
                    shutil.move(file_path, os.path.join(file_folder, file))
                    print(f"Flyttet duplikat: {file_path} til {file_folder}")
                    duplicate_count += 1
                except Exception as e:
                    print(f"Feil ved flytting av duplikat {file_path}: {e}")
            else:
                # Hvis filen ikke er sett før, legg til i ordboken som original
                hashes[file_hash] = {'path': file_path, 'moved': False}

    # Skriv ut totalt antall flyttede duplikater
    print(f"\nTotalt antall flyttede duplikater: {duplicate_count}")


if __name__ == "__main__":
    # Definerer nedlastingsmappen, med støtte for både norske og engelske kataloger
    downloads_folder = os.path.expanduser('~/Nedlastinger')
    if not os.path.isdir(downloads_folder):
        downloads_folder = os.path.expanduser('~/Downloads')

    # Avslutter hvis nedlastingsmappen ikke eksisterer
    if not os.path.isdir(downloads_folder):
        print(f"Den angitte stien {downloads_folder} er ikke en katalog.")
        sys.exit(1)

    # Kjør funksjonen for å finne og flytte duplikater i nedlastingsmappen
    find_duplicates(downloads_folder)
