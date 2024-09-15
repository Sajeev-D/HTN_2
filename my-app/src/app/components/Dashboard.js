import React, { useState } from 'react';

export default function Dashboard() {
  const [file, setFile] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [analysis, setAnalysis] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setVideoId(data.video_id);
      setAnalysis(data.result);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const handleChat = async () => {
    if (!videoId || !chatInput) return;

    try {
      const response = await fetch('http://localhost:5000/conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ video_id: videoId, user_input: chatInput }),
      });
      const data = await response.json();
      setChatHistory([...chatHistory, { user: chatInput, assistant: data.response }]);
      setChatInput('');
    } catch (error) {
      console.error('Error chatting:', error);
    }
  };

  return (
    <div>
      <div className="mb-4">
        <input type="file" onChange={handleFileChange} accept="video/*" className="mb-2" />
        <button onClick={handleUpload} className="bg-blue-500 text-white px-4 py-2 rounded">
          Upload and Analyze
        </button>
      </div>

      {analysis && (
        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-2">Analysis Result:</h2>
          <p>{analysis}</p>
        </div>
      )}
      <div className="mb-4">
        <input
          type="text"
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          placeholder="Ask a question about the video"
          className="w-full p-2 border rounded"
        />
        <button onClick={handleChat} className="bg-purple-500 text-white px-4 py-2 rounded mt-2">
          Ask
        </button>
      </div>
      <div>
        <h2 className="text-xl font-semibold mb-2">Chat History:</h2>
        {chatHistory.map((chat, index) => (
          <div key={index} className="mb-2">
            <p><strong>You:</strong> {chat.user}</p>
            <p><strong>Assistant:</strong> {chat.assistant}</p>
          </div>
        ))}
      </div>
    </div>
  );
}