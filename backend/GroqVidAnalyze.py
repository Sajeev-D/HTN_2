import io
import os
import time
from google.cloud import videointelligence_v1 as videointelligence
from groq import Groq

class ConversationHandler:
    def __init__(self):
        self.client = Groq(api_key=os.environ['GROQ_API_KEY'])
        self.conversation_history = []
        self.system_prompt = ""

    def start_conversation(self, initial_analysis):
        self.system_prompt = f"""You are a video analysis assistant. You have analyzed a video and produced the following analysis:

{initial_analysis}

Based on this analysis, you will now engage in a conversation with the user about the video. Respond to their questions and comments, drawing upon the information in the analysis. If asked about something not covered in the analysis, politely explain that you don't have that information.

Let's begin the conversation."""

        self.conversation_history = []

    def get_response(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history
            ],
            max_tokens=8192,
            temperature=0.5,
        )

        assistant_response = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": assistant_response})

        return assistant_response

def analyze_video(video_path):
    """Analyze a local video file using Google Cloud Video Intelligence API and Groq, and return Groq's analysis as a string."""
    
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

        # [The rest of the video analysis writing code remains unchanged]
        # ... (include all the sections: Label Detection, Face Detection, etc.)

    print(f"\nVideo Intelligence API results saved to {video_analysis_file}")

    # Now process with Groq
    print("Starting Groq analysis...")
    groq_analysis = process_video_analysis(video_analysis_file)

    # Clean up the temporary file
    os.remove(video_analysis_file)

    time_end_read1 = time.time()
    print(f"\nTotal analysis time: {time_end_read1 - time_start_read1:.2f} seconds")

    return groq_analysis

def process_video_analysis(input_file):
    """Process video analysis using Groq and return the result as a string."""
    try:
        client = Groq(api_key=os.environ['GROQ_API_KEY'])
    except KeyError:
        print("GROQ_API_KEY environment variable is not set. Please set it and try again.")
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

    # Make a request to the Groq API
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": custom_prompt,
            }
        ],
        model="mixtral-8x7b-32768",
        max_tokens=8192,
        temperature=0,
        top_p=0.95,
    )

    # Get the response text
    output_text = chat_completion.choices[0].message.content

    print("Groq analysis complete!")
    return output_text

def start_conversation(groq_analysis):
    conversation_handler = ConversationHandler()
    conversation_handler.start_conversation(groq_analysis)
    
    print("\nYou can now start a conversation about the video. Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            print("Conversation ended.")
            break
        
        try:
            response = conversation_handler.get_response(user_input)
            print(f"\nAssistant: {response}")
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try again or type 'exit' to end the conversation.")

def main():
    """Main function to test video analysis and start a conversation."""
    # Set up the path to your test video file
    test_video_path = r"C:\Users\sajee\Videos\Picovoice Screening Interview\intro.mp4"
    
    if not os.path.exists(test_video_path):
        print(f"Error: Test video file not found at {test_video_path}")
        return

    print(f"Starting analysis of {test_video_path}")
    
    try:
        start_time = time.time()
        groq_analysis = analyze_video(test_video_path)
        end_time = time.time()
        print(f"\nAnalysis Result:")
        print(groq_analysis)
        print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")

        # Ask user if they want to start a conversation
        start_chat = input("Do you want to start a conversation about the video? (yes/no): ")
        if start_chat.lower() == 'yes':
            start_time = time.time()
            start_conversation(groq_analysis)
            end_time = time.time()
            print(f"Conversation time: {end_time - start_time:.2f} seconds")
        else:
            print("Conversation not started. Exiting program.")

    except Exception as e:
        print(f"An error occurred during analysis or conversation: {str(e)}")

    input("Press Enter to exit...")

if __name__ == "__main__":
    main()