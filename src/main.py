import os
import shutil
import sqlite3
from mutagen.id3 import ID3, APIC, TALB
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from pydub import AudioSegment
from LibraryMonitor import check_existence, refreshArchive

class FileScan():
    def __init__(self, db_conn, source_dir, target_dir, target_copy_dir):
        self.conn = db_conn
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.target_copy_dir = target_copy_dir

    def scan(self):
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                target_file_path = os.path.join(self.target_copy_dir, file)
                
                # Check if file exists in target directory
                if not check_existence(self.conn, file):
                    # Copy the file
                    shutil.copy2(file_path, target_file_path)
                    print(f"Copied {file_path} to {target_file_path}")
                
                    # Update metadata for copied files
                    set_album_name(target_file_path, os.getenv('ALBUM_NAME'), os.getenv('ARTIST_NAME'))
                    # Optionally, update the database with the new metadata

def set_album_name(file_path, album_name, artist_name):
    try:
        if file_path.lower().endswith('.mp3'):
            mp3 = MP3(file_path)
            mp3['TALB'] = album_name
            mp3['album'] = album_name
            mp3['TPE1'] = artist_name
            mp3['artist'] = artist_name
            mp3.save()
        elif file_path.lower().endswith(('.flac', '.ogg')):
            if file_path.lower().endswith('.flac'):
                flac = FLAC(file_path)
                flac['album'] = album_name
                flac['artist'] = artist_name
                flac.save()
            elif file_path.lower().endswith('.ogg'):
                comment = OggVorbis(file_path)
                comment['album'] = album_name
                comment['artist'] = artist_name
                comment.save()
        else:
            print(f"Unsupported file format: {file_path}")
        print(f"Metadata updated for {file_path}")
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def main():
    # Connect to SQLite database
    conn = sqlite3.connect(os.getenv('DB_FILE'))
    cursor = conn.cursor()

    # Define
    source_directory = os.getenv('SOURCE_DIR')
    target_directory = os.getenv('TARGET_DIR')
    target_copy_dir = os.getenv('TARGET_COPY_DIR')

    # Initialize observer
    scanner = FileScan(conn, source_directory, target_directory, target_copy_dir)
    scanner.scan()
    refreshArchive(target_directory)

if __name__ == "__main__":
    main()
