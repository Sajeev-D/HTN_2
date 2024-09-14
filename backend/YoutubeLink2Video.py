import yt_dlp
import os
from WorkingVid2TextConverter import analyze_video
import time

# Global variable for the download directory
DOWNLOAD_DIR = os.path.join(os.getcwd(), "youtube_downloads")

# Global variable for the downloaded file path (will be set in download_youtube_video function)
DOWNLOADED_FILE_PATH = None

def download_youtube_video(url):
    global DOWNLOADED_FILE_PATH
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # This will download the best quality video with audio
        'merge_output_format': 'mp4',  # Merge video and audio into mp4 format
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Ensure the filename has .mp4 extension
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

def test_youtube_download(youtube_url):
    # Create the download directory if it doesn't exist
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    try:
        print(f"Attempting to download video from: {youtube_url}")
        print(f"Download directory: {DOWNLOAD_DIR}")
        
        file_size = download_youtube_video(youtube_url)
        
        print(f"Video successfully downloaded to: {DOWNLOADED_FILE_PATH}")
        print(f"File size: {file_size:.2f} MB")
        
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    startClock = time.time() # Start timing
    test_youtube_download("https://youtu.be/xjQzg1QAlXs?si=M5Xd7rWn08gl4URK")
    video_path = DOWNLOADED_FILE_PATH
    output_path = r"C:\Users\izcin\OneDrive\Documents\HTN\Video-Audio-To-Text-Generator\backend\videoanalysis.txt"
    analyze_video(video_path, output_path)
    endClock = time.time()  # End timing
    execution_time = endClock - startClock
    print(f"Total execution time: {execution_time:.2f} seconds")


# # Example of how you might use the variables after running the script
# print(f"\nDownload Directory: {DOWNLOAD_DIR}")
# print(f"Full path of downloaded file: {DOWNLOADED_FILE_PATH}")

# if DOWNLOADED_FILE_PATH and os.path.exists(DOWNLOADED_FILE_PATH):
#     print(f"File successfully saved at: {DOWNLOADED_FILE_PATH}")
# else:
#     print("File was not downloaded or cannot be found.")

# print("\nList of files in the download directory:")
# for file in os.listdir(DOWNLOAD_DIR):
#     print(f"- {file}")
    
    # # Test with an invalid URL
    # test_youtube_download("https://www.youtube.com/watch?v=invalid")
    
    # # Test with a non-YouTube URL
    # test_youtube_download("https://www.example.com")
    
    # # Test with a private or unavailable video
    # # (You may need to replace this with an actual unavailable video URL)
    # test_youtube_download("https://www.youtube.com/watch?v=xxxxxxxxxxx")