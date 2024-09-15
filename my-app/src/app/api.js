// api.js

// Mock data for surveillance videos
const mockVideos = [
    {
      id: 1,
      title: "Front Entrance",
      date: "2024-09-14 08:23 AM",
      content: "Delivery person approached with a large package. Resident accepted the delivery."
    },
    {
      id: 2,
      title: "Parking Lot B",
      date: "2024-09-15 11:45 PM",
      content: "Suspicious activity observed. Two individuals examining parked vehicles."
    },
    {
      id: 3,
      title: "Lobby",
      date: "2024-09-16 03:12 PM",
      content: "Argument between two residents over a misplaced package. Security intervened."
    }
  ];
  
  // Mock data for chat messages
  const mockChatMessages = {
    1: [
      { role: 'assistant', content: 'Hello! How can I help you with the Front Entrance footage?' },
      { role: 'user', content: 'What time did the delivery person arrive?' },
      { role: 'assistant', content: 'The delivery person arrived at 08:23 AM.' }
    ],
    2: [
      { role: 'assistant', content: 'Hello! How can I assist you with the Parking Lot B footage?' },
      { role: 'user', content: 'Were any vehicles damaged?' },
      { role: 'assistant', content: 'Based on the footage, no vehicles were breached or damaged.' }
    ],
    3: [
      { role: 'assistant', content: 'Hello! How can I help you with the Lobby incident?' },
      { role: 'user', content: 'Was the situation resolved?' },
      { role: 'assistant', content: 'Yes, the situation was resolved by 03:30 PM after security intervention.' }
    ]
  };
  
  export async function fetchSurveillanceVideos() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockVideos);
      }, 500); // Simulate network delay
    });
  }
  
  export async function fetchChatMessages(videoId) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const messages = mockChatMessages[videoId];
        if (messages) {
          resolve(messages);
        } else {
          reject(new Error('Chat messages not found for this video'));
        }
      }, 500); // Simulate network delay
    });
  }
  
  export async function sendChatMessage(videoId, message) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const response = { message: 'This is a mock response to your query: ' + message };
        resolve(response);
      }, 500); // Simulate network delay
    });
  }