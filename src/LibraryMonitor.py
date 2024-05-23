import os
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
import sqlite3

# Step 2: Setup SQLite Database
def setup_database():
    print("Setting up DB")
    conn = sqlite3.connect(os.getenv('DB_FILE'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS music_files
                 (filename text, title text, artist text, album text, recording_year text)''')
    conn.commit()
    return conn

# Helper function to get metadata based on file extension
def get_metadata(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.mp3':
        return MP3(file_path).tags
    elif ext == '.flac':
        return FLAC(file_path).tags
    elif ext == '.ogg':
        return OggVorbis(file_path).tags
    else:
        return None
    
def check_existence(conn, filename):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM music_files WHERE filename=?", (filename,))
    count = c.fetchone()[0]
    if count == 0:
        return False
    else:
        return True

# Step 3 & 4: Crawl Music Folder and Extract Metadata
def refreshArchive(music_folder):
    conn = sqlite3.connect(os.getenv('DB_FILE'))
    for root, dirs, files in os.walk(music_folder):
        for file in files:
            full_path = os.path.join(root, file)
            filename_only = os.path.basename(full_path)  # Extract just the filename
            metadata = get_metadata(full_path)
            if metadata:
                title = metadata.get('title', [''])[0] if 'title' in metadata else ''
                artist = metadata.get('artist', [''])[0] if 'artist' in metadata else ''
                album = metadata.get('album', [''])[0] if 'album' in metadata else ''
                recording_year = metadata.get('date', [''])[0] if 'date' in metadata else ''
                # Insert metadata into SQLite database
                # Check if the file already exists in the database
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM music_files WHERE filename=?", (filename_only,))
                count = c.fetchone()[0]

                # Only insert if the file does not already exist
                if count == 0:
                    c.execute("INSERT INTO music_files VALUES (?,?,?,?,?)",
                            (filename_only, title, artist, album, recording_year))
                    conn.commit()            
    conn.close()

# Main Function
if __name__ == "__main__":
    # Retrieve the music folder path from the environment variable
    music_folder = os.getenv('TARGET_DIR')
    if music_folder:
        setup_database()
        refreshArchive(music_folder)
    else:
        print("Environment variable 'TARGET_DIR' is not set.")
