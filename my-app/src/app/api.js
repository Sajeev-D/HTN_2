// api.js

// Mock data for surveillance videos
// const mockVideos = [
//     {
//       id: 1,
//       title: "Front Entrance",
//       date: "2024-09-14 08:23 AM",
//       content: "Delivery person approached with a large package. Resident accepted the delivery."
//     },
//     {
//       id: 2,
//       title: "Parking Lot B",
//       date: "2024-09-15 11:45 PM",
//       content: "Suspicious activity observed. Two individuals examining parked vehicles."
//     },
//     {
//       id: 3,
//       title: "Lobby",
//       date: "2024-09-16 03:12 PM",
//       content: "Argument between two residents over a misplaced package. Security intervened."
//     }
//   ];
  
//   // Mock data for chat messages
//   const mockChatMessages = {
//     1: [
//       { role: 'assistant', content: 'Hello! How can I help you with the Front Entrance footage?' },
//       { role: 'user', content: 'What time did the delivery person arrive?' },
//       { role: 'assistant', content: 'The delivery person arrived at 08:23 AM.' }
//     ],
//     2: [
//       { role: 'assistant', content: 'Hello! How can I assist you with the Parking Lot B footage?' },
//       { role: 'user', content: 'Were any vehicles damaged?' },
//       { role: 'assistant', content: 'Based on the footage, no vehicles were breached or damaged.' }
//     ],
//     3: [
//       { role: 'assistant', content: 'Hello! How can I help you with the Lobby incident?' },
//       { role: 'user', content: 'Was the situation resolved?' },
//       { role: 'assistant', content: 'Yes, the situation was resolved by 03:30 PM after security intervention.' }
//     ]
//   };
  
  import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000'; // Adjust this if your backend is on a different port

export async function fetchSurveillanceVideos(email) {
  try {
    const response = await axios.post(`${API_BASE_URL}/footages`, { email });
    return response.data.footages;
  } catch (error) {
    console.error('Error fetching surveillance videos:', error);
    throw error;
  }
}

export async function fetchChatMessages(videoId) {
  try {
    // Note: Your backend doesn't have a specific endpoint for fetching chat messages.
    // You might need to add this endpoint or modify the existing conversation endpoint.
    // For now, we'll return an empty array.
    console.warn('Fetching chat messages is not implemented in the backend.');
    return [];
  } catch (error) {
    console.error('Error fetching chat messages:', error);
    throw error;
  }
}

export async function sendChatMessage(videoId, message) {

  return new Promise((resolve) => {
    setTimeout(() => {
      const response = axios.post(`${API_BASE_URL}/conversation`, {
        video_id: 0,
        user_input: message
      });
      // console.log(response.data);
      resolve(response);
    }, 500); // Simulate network delay
  });
    console.log(videoId) 
    console.log(message)
    const response = await axios.post(`${API_BASE_URL}/conversation`, {
      video_id: 1,
      user_input: message
    });
    console.log(response.data);
    resolve(response);

}