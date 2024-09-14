import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import traceback
from ChromaDB import VideoAnalyzer


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'webm'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

video_analyzer = VideoAnalyzer()

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
            
            video_id, analysis_result = video_analyzer.analyze_video(filepath)
            
            os.remove(filepath)
            
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
        response = video_analyzer.get_conversation_response(video_id, user_input)
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