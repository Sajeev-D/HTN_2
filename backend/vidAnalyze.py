import io
import os
import time
from google.cloud import videointelligence_v1 as videointelligence
import anthropic

def analyze_video(video_path):
    """Analyze a local video file using Google Cloud Video Intelligence API and Claude, and return Claude's analysis as a string."""
    
    time_start_read1 = time.time()

    client = videointelligence.VideoIntelligenceServiceClient()

    # Read the video file
    with io.open(video_path, "rb") as file:
        input_content = file.read()

    # Specify the features you want to analyze
    features = [
        videointelligence.Feature.LABEL_DETECTION,
        videointelligence.Feature.FACE_DETECTION,
        videointelligence.Feature.PERSON_DETECTION,
        videointelligence.Feature.SHOT_CHANGE_DETECTION,
        videointelligence.Feature.OBJECT_TRACKING,
        videointelligence.Feature.SPEECH_TRANSCRIPTION
    ]

    # Set up advanced configuration for some features
    config = videointelligence.VideoContext(
        face_detection_config=videointelligence.FaceDetectionConfig(
            include_bounding_boxes=True,
            include_attributes=True
        ),
        person_detection_config=videointelligence.PersonDetectionConfig(
            include_bounding_boxes=True,
            include_attributes=True,
            include_pose_landmarks=True
        ),
        speech_transcription_config=videointelligence.SpeechTranscriptionConfig(
            language_code="en-US",
            enable_automatic_punctuation=True
        )
    )

    print(f"\nSending video for analysis. This might take a while...")
    operation = client.annotate_video(
        request={
            "features": features,
            "input_content": input_content,
            "video_context": config,
        }
    )

    print("Waiting for operation to complete...")

    result = operation.result(timeout=1200)

    print("\nOperation completed. Processing results...")

    # Generate a unique filename for this analysis
    video_analysis_file = f"video_analysis_{int(time.time())}.txt"
    
    # Process results and write them to the text file
    with open(video_analysis_file, 'w', encoding='utf-8') as f:
        f.write("VIDEO INTELLIGENCE API RESULTS\n\n")

        # 1. Label Detection
        f.write("1. LABEL DETECTION:\n")
        for segment_label in result.annotation_results[0].segment_label_annotations:
            f.write(f"Label: {segment_label.entity.description}\n")
            for segment in segment_label.segments:
                confidence = segment.confidence
                start_time = segment.segment.start_time_offset.total_seconds()
                end_time = segment.segment.end_time_offset.total_seconds()
                f.write(f"\tSegment: {start_time:.2f}s to {end_time:.2f}s (Confidence: {confidence:.2f})\n")
        f.write("\n")

        # 2. Face Detection
        f.write("2. FACE DETECTION:\n")
        for face in result.annotation_results[0].face_detection_annotations:
            for track in face.tracks:
                f.write(f"\tFace detected with confidence: {track.confidence:.2f}\n")
                start_time = track.segment.start_time_offset.total_seconds()
                end_time = track.segment.end_time_offset.total_seconds()
                f.write(f"\tTracked from {start_time:.2f}s to {end_time:.2f}s\n")
                for attribute in track.timestamped_objects[0].attributes:
                    f.write(f"\t\tAttribute: {attribute.name} (Confidence: {attribute.confidence:.2f})\n")
        f.write("\n")

        # 3. Person Detection
        f.write("3. PERSON DETECTION:\n")
        for person in result.annotation_results[0].person_detection_annotations:
            for track in person.tracks:
                f.write(f"\tPerson detected with confidence: {track.confidence:.2f}\n")
                start_time = track.segment.start_time_offset.total_seconds()
                end_time = track.segment.end_time_offset.total_seconds()
                f.write(f"\tTracked from {start_time:.2f}s to {end_time:.2f}s\n")
                for attribute in track.timestamped_objects[0].attributes:
                    f.write(f"\t\tAttribute: {attribute.name} (Confidence: {attribute.confidence:.2f})\n")
        f.write("\n")

        # 4. Shot Change Detection
        f.write("4. SHOT CHANGE DETECTION:\n")
        for i, shot in enumerate(result.annotation_results[0].shot_annotations):
            start_time = shot.start_time_offset.total_seconds()
            end_time = shot.end_time_offset.total_seconds()
            f.write(f"\tShot {i + 1}: {start_time:.2f}s to {end_time:.2f}s\n")
        f.write("\n")

        # 5. Object Tracking
        f.write("5. OBJECT TRACKING:\n")
        for obj in result.annotation_results[0].object_annotations:
            f.write(f"\tTracked object: {obj.entity.description}\n")
            start_time = obj.segment.start_time_offset.total_seconds()
            end_time = obj.segment.end_time_offset.total_seconds()
            f.write(f"\tTracked from {start_time:.2f}s to {end_time:.2f}s\n")
            f.write(f"\tConfidence: {obj.confidence:.2f}\n")
        f.write("\n")

        # 6. Speech Transcription
        f.write("6. SPEECH TRANSCRIPTION:\n")
        for annotation_result in result.annotation_results:
            for speech_transcription in annotation_result.speech_transcriptions:
                for alternative in speech_transcription.alternatives:
                    f.write(f"\tTranscript: {alternative.transcript}\n")
                    f.write(f"\tConfidence: {alternative.confidence:.2f}\n")
                    
                    f.write("\tWord level information:\n")
                    for word_info in alternative.words:
                        start_time = word_info.start_time.total_seconds()
                        end_time = word_info.end_time.total_seconds()
                        f.write(f"\t\t{start_time:.2f}s - {end_time:.2f}s: {word_info.word}\n")
                f.write("\n")

        if not any(annotation_result.speech_transcriptions for annotation_result in result.annotation_results):
            f.write("\tNo speech transcriptions found.\n")
            print("No speech transcriptions were returned by the API.")
            print("Possible reasons:")
            print("- The video might not have an audio track")
            print("- The audio quality might be poor")
            print("- The speech might be in a different language than specified")
            print("- There might be an issue with the API request or response")

    print(f"\nVideo Intelligence API results saved to {video_analysis_file}")

    # Now process with Claude
    print("Starting Claude analysis...")
    claude_analysis = process_video_analysis(video_analysis_file)

    # Clean up the temporary file
    os.remove(video_analysis_file)

    time_end_read1 = time.time()
    print(f"\nTotal analysis time: {time_end_read1 - time_start_read1:.2f} seconds")

    return claude_analysis

def process_video_analysis(input_file):
    """Process video analysis using Claude and return the result as a string."""
    try:
        client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    except KeyError:
        print("ANTHROPIC_API_KEY environment variable is not set. Please set it and try again.")
        return None

    # Read the video analysis file
    with open(input_file, 'r', encoding='utf-8') as file:
        video_analysis = file.read()

    # Custom prompt
    custom_prompt = f"""You are a video consultant tasked with describing and analyzing a video based on provided analysis data. Your goal is to create a comprehensive description of the video's content and conclude with its main story.

        Here is the video analysis data:
        <video_analysis>
        {video_analysis}
        </video_analysis>

        Based on this data, please provide:
        1. A detailed description of the video's content, including:
           - Main objects and people detected
           - Key actions and events
           - Any text or speech detected
           - Descriptions of different scenes or shots
        2. An analysis of the video's main theme or story
        3. Any notable or interesting observations about the video

        Please be as specific and detailed as possible in your description and analysis.
        """

    # Create the message for Claude
    messages = [
        {"role": "user", "content": custom_prompt}
    ]

    # Make a request to the Anthropic API
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=8192,
        temperature=0,
        top_p=0.95,
        messages=messages,
        extra_headers={"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"}
    )

    # Get the response text
    output_text = response.content[0].text

    print("Claude analysis complete!")
    return output_text

def main():
    """Main function to test video analysis."""
    # Set up the path to your test video file
    test_video_path = r"C:\Users\sajee\Videos\Picovoice Screening Interview\intro.mp4"
    
    if not os.path.exists(test_video_path):
        print(f"Error: Test video file not found at {test_video_path}")
        return

    print(f"Starting analysis of {test_video_path}")
    
    try:
        result = analyze_video(test_video_path)
        print("\nAnalysis Result:")
        print(result)
    except Exception as e:
        print(f"An error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    main()

# Masv
# Groq


## Last day
# Godaddy