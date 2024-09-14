import io
import os
import time
from google.cloud import videointelligence_v1 as videointelligence
from groq import Groq
import chromadb

class VideoAnalyzer:
    def __init__(self):
        self.client = videointelligence.VideoIntelligenceServiceClient()
        self.groq_client = Groq(api_key=os.environ['GROQ_API_KEY'])
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="video_analysis")

    def analyze_video(self, video_path):
        with io.open(video_path, "rb") as file:
            input_content = file.read()

        features = [
            videointelligence.Feature.LABEL_DETECTION,
            videointelligence.Feature.FACE_DETECTION,
            videointelligence.Feature.PERSON_DETECTION,
            videointelligence.Feature.SHOT_CHANGE_DETECTION,
            videointelligence.Feature.OBJECT_TRACKING,
            videointelligence.Feature.SPEECH_TRANSCRIPTION
        ]

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

        operation = self.client.annotate_video(
            request={
                "features": features,
                "input_content": input_content,
                "video_context": config,
            }
        )

        result = operation.result(timeout=1200)

        video_id = f"video_{int(time.time())}"
        
        sections = [
            ("LABEL_DETECTION", result.annotation_results[0].segment_label_annotations),
            ("FACE_DETECTION", result.annotation_results[0].face_detection_annotations),
            ("PERSON_DETECTION", result.annotation_results[0].person_detection_annotations),
            ("SHOT_CHANGE_DETECTION", result.annotation_results[0].shot_annotations),
            ("OBJECT_TRACKING", result.annotation_results[0].object_annotations),
            ("SPEECH_TRANSCRIPTION", result.annotation_results[0].speech_transcriptions)
        ]

        for section_name, section_data in sections:
            section_text = self.process_section(section_name, section_data)
            self.collection.add(
                documents=[section_text],
                metadatas=[{"video_id": video_id, "section": section_name}],
                ids=[f"{video_id}_{section_name}"]
            )

        groq_analysis = self.process_video_analysis(video_id)
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

    def process_video_analysis(self, video_id):
        results = self.collection.query(
            query_texts=[f"Video analysis for {video_id}"],
            n_results=10
        )
        
        documents = [item for sublist in results['documents'] for item in (sublist if isinstance(sublist, list) else [sublist])]
        documents = [doc for doc in documents if isinstance(doc, str)]
        
        if not documents:
            return None

        video_analysis = "\n\n".join(documents)
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

        chat_completion = self.groq_client.chat.completions.create(
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

        output_text = chat_completion.choices[0].message.content

        self.collection.add(
            documents=[output_text],
            metadatas=[{"video_id": video_id, "section": "GROQ_ANALYSIS"}],
            ids=[f"{video_id}_GROQ_ANALYSIS"]
        )

        return output_text

    def get_conversation_response(self, video_id, user_input):
        results = self.collection.query(
            query_texts=[user_input],
            n_results=3
        )
        
        documents = [item for sublist in results['documents'] for item in (sublist if isinstance(sublist, list) else [sublist])]
        documents = [doc for doc in documents if isinstance(doc, str)]
        
        relevant_info = "\n".join(documents) if documents else "No relevant information found."

        system_prompt = f"""You are a video analysis assistant. You have analyzed a video with ID {video_id}. 
        Based on this analysis, you will now engage in a conversation with the user about the video. 
        Respond to their questions and comments, drawing upon the information in the analysis. 
        If asked about something not covered in the analysis, politely explain that you don't have that information."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"Additional relevant information:\n{relevant_info}"},
            {"role": "user", "content": user_input}
        ]

        try:
            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=messages,
                max_tokens=8192,
                temperature=0.5,
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in Groq API call: {str(e)}")
            return "I'm sorry, but I encountered an error while processing your request. Could you please try asking your question in a different way?"