'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { fetchChatMessages, sendChatMessage } from '../api';

export default function ChatPage({ params }) {
  const router = useRouter();
  const { id } = params;
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  useEffect(() => {
    const loadChatMessages = async () => {
      try {
        const chatMessages = await fetchChatMessages(id);
        setMessages(chatMessages);
      } catch (error) {
        console.error('Failed to load chat messages:', error);
        // Handle error (e.g., show error message to user)
      }
    };

    loadChatMessages();
  }, [id]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (input.trim()) {
      const newUserMessage = { role: 'user', content: input };
      setMessages(prev => [...prev, newUserMessage]);
      setInput('');

      try {
        const response = await sendChatMessage(id, input);
        setMessages(prev => [...prev, { role: 'assistant', content: response.message }]);
      } catch (error) {
        console.error('Failed to send message:', error);
        // Handle error (e.g., show error message to user)
      }
    }
  };
  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <header className="bg-blue-600 text-white p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">Chat about Surveillance ID: {id}</h1>
        <button
          onClick={() => router.push('/')}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Back to Dashboard
        </button>
      </header>
      <div className="flex-grow overflow-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-sm p-3 rounded-lg ${message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-white'}`}>
              {message.content}
            </div>
          </div>
        ))}
      </div>
      <form onSubmit={handleSendMessage} className="p-4 bg-white border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message here..."
            className="flex-grow p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition duration-300"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}