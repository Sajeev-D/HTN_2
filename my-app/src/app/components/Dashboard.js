import React, { useState } from 'react';
import { useUser } from '@auth0/nextjs-auth0/client';

export default function Dashboard() {
  const [file, setFile] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [analysis, setAnalysis] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const { user, error, isLoading } = useUser();
  const [label, setLabel] = useState('');
  const [name, setName] = useState('');

  console.log(user.email);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('label', label);
    formData.append('name', name);

    try {
      // Upload and analyze the file
      const analyzeResponse = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        body: formData,
      });
      const analyzeData = await analyzeResponse.json();
      setVideoId(analyzeData.video_id);
      setAnalysis(analyzeData.result);
      setLabel(analyzeData.label);
      setName(analyzeData.name);

      // Save user data
      const saveUserResponse = await fetch('http://localhost:5000/api/save-user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: user.email,
          name: name,
          label: label
        }),
      });

      if (!saveUserResponse.ok) {
        console.error('Failed to save user data');
      }

    } catch (error) {
      console.error('Error during upload or saving user data:', error);
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
        <input
          type="text"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          placeholder="Enter label"
          className="w-full p-2 border rounded mb-2"
        />
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter name"
          className="w-full p-2 border rounded mb-2"
        />
        <input type="file" onChange={handleFileChange} accept="video/*" className="mb-2" />
        <button onClick={handleUpload} className="bg-blue-500 text-white px-4 py-2 rounded">
          Upload and Analyze
        </button>
      </div>

      {analysis && (
        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-2">Analysis Result:</h2>
          <p>{analysis}</p>
          <p><strong>Label:</strong> {label}</p>
          <p><strong>Name:</strong> {name}</p>
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