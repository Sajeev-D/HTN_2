'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Camera } from 'lucide-react';

const ChatItem = ({ id, title, date, content }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const previewLength = 100;
  const router = useRouter();

  const toggleExpand = (e) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden border border-gray-200 flex">
      <div className="p-4 bg-gray-50 w-1/3 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold text-blue-600 text-lg">{title}</h3>
            <Camera size={20} className="text-blue-500" />
          </div>
          <p className="text-sm text-gray-600">{date}</p>
        </div>
        <div className="flex space-x-2">
          <button
            className="mt-4 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-full text-sm transition duration-300 ease-in-out transform hover:scale-105"
            onClick={() => {}} // Implement view footage functionality
          >
            View Footage
          </button>
          <button
            className="mt-4 bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded-full text-sm transition duration-300 ease-in-out transform hover:scale-105"
            onClick={() => router.push(`/chatpage`)}
          >
            Chat
          </button>
        </div>
      </div>
      <div className="p-4 w-2/3 border-l border-gray-200">
        <div className="text-gray-700 mb-2 font-light">
          {isExpanded ? content : `${content.slice(0, previewLength)}...`}
        </div>
        <button
          className="text-blue-500 hover:text-blue-600 flex items-center text-sm font-light"
          onClick={toggleExpand}
        >
          {isExpanded ? 'Show less' : 'Show more'}
        </button>
      </div>
    </div>
  );
};

const ClientChatList = () => {
  const hardCodedChats = [
    {
      id: 1,
      title: "Front Entrance - Morning",
      date: "2023-09-15 08:00 AM",
      content: "Surveillance footage of the front entrance during morning hours. Several employees entered the building between 8:00 AM and 9:00 AM. No suspicious activities observed."
    },
    {
      id: 2,
      title: "Parking Lot - Afternoon",
      date: "2023-09-15 02:30 PM",
      content: "Footage of the main parking lot during afternoon hours. Regular vehicle traffic observed. A delivery truck arrived at 2:45 PM and left at 3:00 PM after unloading packages."
    },
    {
      id: 3,
      title: "Back Alley - Night",
      date: "2023-09-15 11:45 PM",
      content: "Night vision footage of the back alley. A stray cat was observed at 11:52 PM. No human activity detected during this period."
    },
    {
      id: 4,
      title: "Server Room - Maintenance",
      date: "2023-09-16 03:15 AM",
      content: "Footage of scheduled maintenance in the server room. Two IT personnel entered at 3:15 AM and left at 4:30 AM. All activities appeared routine and authorized."
    },
    {
      id: 5,
      title: "Main Lobby - Lunch Hour",
      date: "2023-09-16 12:00 PM",
      content: "Surveillance of the main lobby during lunch hours. High foot traffic observed between 12:00 PM and 1:00 PM. No incidents reported."
    }
  ];

  return (
    <div className="space-y-6 overflow-y-auto max-h-[calc(100vh-8rem)]">
      {hardCodedChats.map((chat) => (
        <ChatItem key={chat.id} {...chat} />
      ))}
    </div>
  );
};

const Dashboard = () => {
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
    <div className="space-y-6">
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
      <div className="overflow-y-auto max-h-[calc(100vh-24rem)]">
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
};

export default function SurveillancePage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-100 text-black font-[family-name:var(--font-geist-sans)]">
      <main className="max-w-7xl mx-auto p-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Surveillance Dashboard</h1>
        </div>
        <div className="flex gap-8">
          <div className="w-1/2">
            <h2 className="text-2xl font-semibold mb-4 text-gray-700">Surveillance Videos</h2>
            <ClientChatList />
          </div>
          <div className="w-1/2">
            <h2 className="text-2xl font-semibold mb-4 text-gray-700">Video Analysis</h2>
            <Dashboard />
          </div>
        </div>
      </main>
    </div>
  );
}