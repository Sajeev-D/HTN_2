import yt_dlp
import os
import time
from ChromaDb import analyze_video, start_conversation
import chromadb

# Global variables
DOWNLOAD_DIR = os.path.join(os.getcwd(), "youtube_downloads")
DOWNLOADED_FILE_PATH = None

def download_youtube_video(url):
    global DOWNLOADED_FILE_PATH
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not filename.endswith('.mp4'):
                filename = os.path.splitext(filename)[0] + '.mp4'
            
            DOWNLOADED_FILE_PATH = os.path.abspath(filename)
            
            if not os.path.exists(DOWNLOADED_FILE_PATH):
                raise FileNotFoundError(f"Expected file {DOWNLOADED_FILE_PATH} not found")

            file_size = os.path.getsize(DOWNLOADED_FILE_PATH) / (1024 * 1024)  # Size in MB
            
            return file_size

    except yt_dlp.utils.DownloadError as e:
        if "Private video" in str(e):
            raise ValueError("This video is private")
        elif "This video is unavailable" in str(e):
            raise ValueError("This video is unavailable")
        else:
            raise ValueError(f"Error downloading video: {str(e)}")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {str(e)}")

def process_youtube_video(youtube_url):
    # Set up ChromaDB
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection_name = "video_analysis"
    collection = chroma_client.get_or_create_collection(name=collection_name)

    # Create the download directory if it doesn't exist
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    try:
        print(f"Attempting to download video from: {youtube_url}")
        print(f"Download directory: {DOWNLOAD_DIR}")
        
        file_size = download_youtube_video(youtube_url)
        
        print(f"Video successfully downloaded to: {DOWNLOADED_FILE_PATH}")
        print(f"File size: {file_size:.2f} MB")
        
        # Analyze the video
        start_time = time.time()
        video_id, groq_analysis = analyze_video(DOWNLOADED_FILE_PATH, collection)
        end_time = time.time()
        
        if groq_analysis is None:
            print("Failed to generate Groq analysis. Exiting.")
            return
        
        print(f"\nAnalysis Result:")
        print(groq_analysis)
        print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")

        # Ask user if they want to start a conversation
        start_chat = input("Do you want to start a conversation about the video? (yes/no): ")
        if start_chat.lower() == 'yes':
            start_time = time.time()
            start_conversation(video_id, groq_analysis, collection)
            end_time = time.time()
            print(f"Conversation time: {end_time - start_time:.2f} seconds")
        else:
            print("Conversation not started. Exiting program.")
        
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    youtube_url = input("Enter the YouTube URL: ")
    process_youtube_video(youtube_url)