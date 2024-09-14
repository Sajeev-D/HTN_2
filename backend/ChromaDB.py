import io
import os
import time
from google.cloud import videointelligence_v1 as videointelligence
from groq import Groq
import chromadb
class ConversationHandler:
    def __init__(self, collection):
        self.client = Groq(api_key=os.environ['GROQ_API_KEY'])
        self.conversation_history = []
        self.system_prompt = ""
        self.collection = collection

    def start_conversation(self, video_id, initial_analysis):
        # Retrieve the stored analysis from ChromaDB
        results = self.collection.query(
            query_texts=[f"Video analysis for {video_id}"],
            n_results=1
        )
        
        print(f"Start conversation query results: {results}")  # Debug print
        
        if results['documents'] and isinstance(results['documents'][0], list):
            stored_analysis = results['documents'][0][0] if results['documents'][0] else initial_analysis
        elif results['documents']:
            stored_analysis = results['documents'][0]
        else:
            stored_analysis = initial_analysis

        if stored_analysis != initial_analysis:
            # Store the analysis in ChromaDB if it's not already there
            self.collection.add(
                documents=[stored_analysis],
                metadatas=[{"video_id": video_id}],
                ids=[f"analysis_{video_id}"]
            )

        self.system_prompt = f"""You are a video analysis assistant. You have analyzed a video and produced the following analysis:

{stored_analysis}

Based on this analysis, you will now engage in a conversation with the user about the video. Respond to their questions and comments, drawing upon the information in the analysis. If asked about something not covered in the analysis, politely explain that you don't have that information.

Let's begin the conversation."""

        self.conversation_history = []

    def get_response(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})

        # Query ChromaDB for relevant information
        results = self.collection.query(
            query_texts=[user_input],
            n_results=3
        )
        
        print(f"Query results: {results}")  # Debug print

        # Process and flatten the documents
        documents = []
        for doc in results['documents']:
            if isinstance(doc, list):
                documents.extend(doc)
            elif isinstance(doc, str):
                documents.append(doc)
        
        relevant_info = "\n".join(documents) if documents else "No relevant information found."

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": f"Additional relevant information:\n{relevant_info}"},
            *self.conversation_history
        ]

        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=messages,
                max_tokens=8192,
                temperature=0.5,
            )

            assistant_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_response})

            return assistant_response
        except Exception as e:
            print(f"Error in Groq API call: {str(e)}")
            return "I'm sorry, but I encountered an error while processing your request. Could you please try asking your question in a different way?"
        

def analyze_video(video_path, collection):
    """Analyze a local video file using Google Cloud Video Intelligence API and Groq, and store the results in ChromaDB."""
    
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

    # Generate a unique identifier for this video
    video_id = f"video_{int(time.time())}"
    
    # Store each section of the analysis separately
    sections = [
        ("LABEL_DETECTION", result.annotation_results[0].segment_label_annotations),
        ("FACE_DETECTION", result.annotation_results[0].face_detection_annotations),
        ("PERSON_DETECTION", result.annotation_results[0].person_detection_annotations),
        ("SHOT_CHANGE_DETECTION", result.annotation_results[0].shot_annotations),
        ("OBJECT_TRACKING", result.annotation_results[0].object_annotations),
        ("SPEECH_TRANSCRIPTION", result.annotation_results[0].speech_transcriptions)
    ]

    for section_name, section_data in sections:
        section_text = process_section(section_name, section_data)
        collection.add(
            documents=[section_text],
            metadatas=[{"video_id": video_id, "section": section_name}],
            ids=[f"{video_id}_{section_name}"]
        )

    print(f"\nVideo Intelligence API results stored in ChromaDB")

    # Now process with Groq
    print("Starting Groq analysis...")
    groq_analysis = process_video_analysis(video_id, collection)

    time_end_read1 = time.time()
    print(f"\nTotal analysis time: {time_end_read1 - time_start_read1:.2f} seconds")

    return video_id, groq_analysis

def process_section(section_name, section_data):
    """Process each section of the video analysis"""
    if section_name == "LABEL_DETECTION":
        return process_label_detection(section_data)
    elif section_name == "FACE_DETECTION":
        return process_face_detection(section_data)
    elif section_name == "PERSON_DETECTION":
        return process_person_detection(section_data)
    elif section_name == "SHOT_CHANGE_DETECTION":
        return process_shot_change_detection(section_data)
    elif section_name == "OBJECT_TRACKING":
        return process_object_tracking(section_data)
    elif section_name == "SPEECH_TRANSCRIPTION":
        return process_speech_transcription(section_data)
    else:
        return f"{section_name}:\n{str(section_data)}"

def process_label_detection(label_annotations):
    result = "LABEL DETECTION:\n"
    for label in label_annotations:
        result += f"Label: {label.entity.description}\n"
        for segment in label.segments:
            confidence = segment.confidence
            start_time = segment.segment.start_time_offset.total_seconds()
            end_time = segment.segment.end_time_offset.total_seconds()
            result += f"  Segment: {start_time:.2f}s to {end_time:.2f}s (Confidence: {confidence:.2f})\n"
    return result

def process_face_detection(face_annotations):
    result = "FACE DETECTION:\n"
    for face in face_annotations:
        for track in face.tracks:
            result += f"Face detected with confidence: {track.confidence:.2f}\n"
            start_time = track.segment.start_time_offset.total_seconds()
            end_time = track.segment.end_time_offset.total_seconds()
            result += f"  Tracked from {start_time:.2f}s to {end_time:.2f}s\n"
            for attribute in track.timestamped_objects[0].attributes:
                result += f"    Attribute: {attribute.name} (Confidence: {attribute.confidence:.2f})\n"
    return result

def process_person_detection(person_annotations):
    result = "PERSON DETECTION:\n"
    for person in person_annotations:
        for track in person.tracks:
            result += f"Person detected with confidence: {track.confidence:.2f}\n"
            start_time = track.segment.start_time_offset.total_seconds()
            end_time = track.segment.end_time_offset.total_seconds()
            result += f"  Tracked from {start_time:.2f}s to {end_time:.2f}s\n"
            for attribute in track.timestamped_objects[0].attributes:
                result += f"    Attribute: {attribute.name} (Confidence: {attribute.confidence:.2f})\n"
    return result

def process_shot_change_detection(shot_annotations):
    result = "SHOT CHANGE DETECTION:\n"
    for i, shot in enumerate(shot_annotations):
        start_time = shot.start_time_offset.total_seconds()
        end_time = shot.end_time_offset.total_seconds()
        result += f"  Shot {i + 1}: {start_time:.2f}s to {end_time:.2f}s\n"
    return result

def process_object_tracking(object_annotations):
    result = "OBJECT TRACKING:\n"
    for obj in object_annotations:
        result += f"Tracked object: {obj.entity.description}\n"
        start_time = obj.segment.start_time_offset.total_seconds()
        end_time = obj.segment.end_time_offset.total_seconds()
        result += f"  Tracked from {start_time:.2f}s to {end_time:.2f}s\n"
        result += f"  Confidence: {obj.confidence:.2f}\n"
    return result

def process_speech_transcription(speech_transcriptions):
    result = "SPEECH TRANSCRIPTION:\n"
    for speech_transcription in speech_transcriptions:
        for alternative in speech_transcription.alternatives:
            result += f"Transcript: {alternative.transcript}\n"
            result += f"Confidence: {alternative.confidence:.2f}\n"
            result += "Word level information:\n"
            for word_info in alternative.words:
                start_time = word_info.start_time.total_seconds()
                end_time = word_info.end_time.total_seconds()
                result += f"  {start_time:.2f}s - {end_time:.2f}s: {word_info.word}\n"
    return result

def process_video_analysis(video_id, collection):
    """Process video analysis using Groq and store the result in ChromaDB."""
    try:
        client = Groq(api_key=os.environ['GROQ_API_KEY'])
    except KeyError:
        print("GROQ_API_KEY environment variable is not set. Please set it and try again.")
        return None

    # Retrieve all sections of the video analysis from ChromaDB
    results = collection.query(
        query_texts=[f"Video analysis for {video_id}"],
        n_results=10  # Adjust this number based on how many sections you have
    )
    
    print(f"Query results: {results}")  # Debug print
    
    # Check if 'documents' is in results and is a list
    if 'documents' not in results or not isinstance(results['documents'], list):
        print(f"Unexpected result structure: {results}")
        return None

    # Flatten the list of documents if it's a nested list
    documents = [item for sublist in results['documents'] for item in (sublist if isinstance(sublist, list) else [sublist])]
    
    # Filter out any non-string items
    documents = [doc for doc in documents if isinstance(doc, str)]
    
    if not documents:
        print("No valid documents found in the query results.")
        return None

    video_analysis = "\n\n".join(documents)
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

    # Store the Groq analysis in ChromaDB
    collection.add(
        documents=[output_text],
        metadatas=[{"video_id": video_id, "section": "GROQ_ANALYSIS"}],
        ids=[f"{video_id}_GROQ_ANALYSIS"]
    )

    print("Groq analysis complete and stored in ChromaDB!")
    return output_text

def start_conversation(video_id, groq_analysis, collection):
    conversation_handler = ConversationHandler(collection)
    conversation_handler.start_conversation(video_id, groq_analysis)
    
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
    # Set up ChromaDB
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection_name = "video_analysis"

    # Get or create the collection
    collection = chroma_client.get_or_create_collection(name=collection_name)

    # Set up the path to your test video file
    test_video_path = r"C:\Users\izcin\OneDrive\Documents\HTN\Video-Audio-To-Text-Generator\backend\youtube_downloads\Video.mp4"
    
    if not os.path.exists(test_video_path):
        print(f"Error: Test video file not found at {test_video_path}")
        return

    print(f"Starting analysis of {test_video_path}")
    
    try:
        start_time = time.time()
        video_id, groq_analysis = analyze_video(test_video_path, collection)
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

    except Exception as e:
        print(f"An error occurred during analysis or conversation: {str(e)}")
        import traceback
        traceback.print_exc()  # This will print the full stack trace

    input("Press Enter to exit...")

if __name__ == "__main__":
    main()