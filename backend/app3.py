import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import traceback
import chromadb
import boto3
from botocore.exceptions import ClientError
from ChromaDB import analyze_video, ConversationHandler
from flask_pymongo import PyMongo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

session = boto3.Session(
    aws_access_key_id='AKIA2RP6IM4AKQECXWEH',
    aws_secret_access_key='fMlh58nedpQvELEGV6kYzzKc/MHZNw03pNgRdAFZ',
    region_name='us-east-2'  # e.g., 'us-west-2'
)

dynamodb = session.resource('dynamodb', region_name='us-east-2')  # e.g., 'us-east-1'
table = dynamodb.Table('footagedb')  # Replace 'Users' with your table name

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

def user_exists(email):
    try:
        response = table.get_item(
            Key={
                'email': email
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False
    else:
        return 'Item' in response

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    label = request.form.get('label', '')
    name = request.form.get('name', '')
    
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
            
            return jsonify({
                'video_id': video_id, 
                'result': analysis_result,
                'label': label,
                'name': name
            }), 200
        except Exception as e:
            app.logger.error(f"Error during video analysis: {str(e)}")
            app.logger.error(traceback.format_exc())
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'File type not allowed'}), 400
    
# Return the label and name of the video

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

@app.route('/api/save-user', methods=['POST'])
def save_user():
    user_data = request.json

    # Extract email and other details from the request
    email = user_data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    print("before")
    # Check if the user already exists in DynamoDB
    exists = user_exists(email)

    print("after")
    if not exists:
        print("User doesn't exist yet")
        # If user doesn't exist, create a new user record
        new_user = {
            'email': email,
            'footage': []
        }
        try:
            table.put_item(Item=new_user)
            return jsonify({'message': 'User created'}), 201
        except Exception as e:
            return jsonify({'error': f"Error creating user: {str(e)}"}), 500
    else:
        return jsonify({'message': 'User already exists'}), 200

@app.route('/api/add-footage', methods=['POST'])
def add_footage():
    user_data = request.json
    email = user_data.get('email')
    label = user_data.get('label')
    name = user_data.get('name')
    # video_id = user_data.get('video_id')
    analysis = user_data.get('analysis')

    if not email or not label:
        return jsonify({'error': 'Email and footage data are required'}), 400

    # Find the user by email
    exists = user_exists(email)

    if exists:
        # Append the new footage to the user's footage list
        new_footage = {
            'label': label,
            'name': name,
            'upload_date': datetime.utcnow().isoformat(),
            'analysis': analysis
        }

        try:
            # Update the user's record by appending the new footage to the existing list
            response = table.update_item(
                Key={'email': email},
                UpdateExpression="SET #footage = list_append(if_not_exists(#footage, :empty_list), :new_footage)",
                ExpressionAttributeNames={'#footage': 'footage'},
                ExpressionAttributeValues={
                    ':new_footage': [new_footage],
                    ':empty_list': []
                },
                ReturnValues="UPDATED_NEW"
            )
            return jsonify({'message': 'Footage added successfully'}), 200
        except ClientError as e:
            print(e.response['Error']['Message'])
            return jsonify({'error': 'Failed to add footage'}), 500
    else:
        return jsonify({'error': 'User not found'}), 404

def get_user(email):
    try:
        response = table.get_item(Key={'email': email})
        return response.get('Item')
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None

@app.route('/footages', methods=['POST'])
def get_footages():
    user_data = request.json
    email = user_data.get('email')  # Use .get() method to safely access 'email'

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Find the user by email
        user = get_user(email)

        if user and 'footage' in user:
            return jsonify({"footages": user['footage']}), 200
        else:
            return jsonify({"footages": []}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)