import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import traceback
import chromadb
from ChromaDB import analyze_video, ConversationHandler

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'webm'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize ChromaDB client and collection
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="video_analysis")

# Create a ConversationHandler instance
conversation_handler = ConversationHandler(collection)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            video_id, analysis_result = analyze_video(filepath, collection)
            
            os.remove(filepath)
            
            # Start a new conversation for this video
            conversation_handler.start_conversation(video_id, analysis_result)
            
            return jsonify({'video_id': video_id, 'result': analysis_result}), 200
        except Exception as e:
            app.logger.error(f"Error during video analysis: {str(e)}")
            app.logger.error(traceback.format_exc())
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/conversation', methods=['POST'])
def conversation():
    data = request.json
    if not data or 'video_id' not in data or 'user_input' not in data:
        return jsonify({'error': 'Missing video_id or user_input'}), 400

    video_id = data['video_id']
    user_input = data['user_input']

    try:
        # Ensure the conversation is started for this video_id
        if video_id not in conversation_handler.conversation_history:
            # Retrieve the analysis from ChromaDB
            results = collection.query(
                query_texts=[f"Video analysis for {video_id}"],
                n_results=1
            )
            if results['documents'] and isinstance(results['documents'][0], list):
                analysis = results['documents'][0][0]
            elif results['documents']:
                analysis = results['documents'][0]
            else:
                return jsonify({'error': 'Video analysis not found'}), 404
            
            conversation_handler.start_conversation(video_id, analysis)

        response = conversation_handler.get_response(user_input)
        return jsonify({'response': response}), 200
    except Exception as e:
        app.logger.error(f"Error during conversation: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large (max 100MB)'}), 413

if __name__ == '__main__':
    app.run(debug=True)