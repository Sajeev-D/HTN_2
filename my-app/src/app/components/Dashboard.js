'use client';

import React, { useState, useEffect } from 'react';
import { useUser } from '@auth0/nextjs-auth0/client';
import { useRouter } from 'next/navigation';
import { Camera } from 'lucide-react';
import chatStore from '../chatStore';

const ChatItem = ({ id, name, label, upload_date, analysis }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const previewLength = 100;
  const router = useRouter();

  const toggleExpand = (e) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  const handleChatClick = () => {
    chatStore.setCurrentChatId(id);
    router.push('/chatpage');
  };

  // Format the date
  const formattedDate = new Date(upload_date).toLocaleString();

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden border border-gray-200 flex">
      <div className="p-4 bg-gray-50 w-1/3 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold text-blue-600 text-lg">{name || 'Untitled'}</h3>
            <Camera size={20} className="text-blue-500" />
          </div>
          <p className="text-sm text-gray-600">{formattedDate}</p>
          <p className="text-sm text-gray-600 mt-1">Label: {label || 'Unlabeled'}</p>
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
            onClick={handleChatClick}
          >
            Chat
          </button>
        </div>
      </div>
      <div className="p-4 w-2/3 border-l border-gray-200">
        <div className="text-gray-700 mb-2 font-light">
          {isExpanded ? analysis : `${analysis.slice(0, previewLength)}...`}
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
  const [chats, setChats] = useState([]);
  const [labelLog, setLabelLog] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user } = useUser();

  useEffect(() => {
    const fetchChats = async () => {
      if (!user || !user.email) return;

      setIsLoading(true);
      try {
        const response = await fetch('http://localhost:5000/footages', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email: user.email }),
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch footages');
        }
        
        const data = await response.json();
        console.log(data);
        setChats(data.footages || []);
        
        // Create label log
        const log = (data.footages || []).reduce((acc, footage) => {
          if (footage.label) {
            acc[footage.label] = (acc[footage.label] || 0) + 1;
          }
          return acc;
        }, {});
        setLabelLog(log);
      } catch (err) {
        console.error('Error fetching footages:', err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchChats();
  }, [user]);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-2">Label Log</h3>
        <ul className="bg-white rounded-lg shadow p-4">
          {Object.entries(labelLog).map(([label, count]) => (
            <li key={label} className="mb-2">
              <span className="font-medium">{label}:</span> {count} occurrence{count !== 1 ? 's' : ''}
            </li>
          ))}
        </ul>
      </div>
      <div className="space-y-6 overflow-y-auto max-h-[calc(100vh-16rem)]">
        {chats.map((chat) => (
          <ChatItem key={chat.id} {...chat} />
        ))}
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [file, setFile] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [analysis, setAnalysis] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const { user, error, isLoading } = useUser();
  const [label, setLabel] = useState('');
  const [name, setName] = useState('');

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
      const saveUserResponse = await fetch('http://localhost:5000/api/add-footage', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: user.email,
          name: name,
          label: label,
          analysis: analyzeData.result
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
    <div className="space-y-6">
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

const SurveillancePage = () => {
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
};

export default SurveillancePage;