'use client';

import React, { useState } from 'react';
import { useUser } from '@auth0/nextjs-auth0/client';

export default function Index() {
  const {user, error, isLoading } = useUser();
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
      setAnalysis(data.result);  // Changed from data.analysis to data.result
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

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>{error.message}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Video Analysis Tool</h1>
      {user ? (
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
      ) : (
        <a href="/api/auth/login" className="bg-blue-500 text-white px-4 py-2 rounded">
          Log in
        </a>
      )}
    </div>
  );
}


  // // Stores the selected file in the component state using setFile
  // const handleFileChange = (event) => {
  //   setFile(event.target.files[0]);
  // };

  // const handleUpload = async () => {
  //   if (!file) return;

  //   const formData = new FormData();
  //   formData.append('file', file);

  //   try {
  //     const response = await fetch('http://localhost:5000/process-video', {
  //       method: 'POST',
  //       body: formData,
  //     });
  //     const data = await response.json();
  //     setVideoId(data.video_id);
  //     setAnalysis(data.analysis);
  //   } catch (error) {
  //     console.error('Error uploading file:', error);
  //   }
  // };


  // /****************************** For MASV Uploader***************************/

  // const [portalSubdomain, setPortalSubdomain] = useState('sajeevsteamportal3224351131'); // fixed
  // const [uploader, setUploader] = useState(null);
  // const [uploadProgress, setUploadProgress] = useState(0);
  // const MASV_API_KEY = 'FH:ET*6Ad95bVJ3SmavDXOUCLhtY+Nci!zxf0)pW14,=n<gGsy$PIuZ-j8r72kKM';

  // async function fetchPortalID(subdomain) { 
  //   const response = await fetch(`https://api.massive.app/v1/subdomains/portals/${subdomain}`, {
  //     headers: {
  //       'Authorization': `Bearer ${MASV_API_KEY}`
  //     }
  //   });
  //   const { id } = await response.json();
  //   return id;
  // }
  
  // async function createPackage(portalID) {  
  //   const response = await fetch(`https://api.massive.app/v1/portals/${portalID}/packages`, {
  //     method: "POST",
  //     headers: { 
  //       "Content-Type": "application/json",
  //       'Authorization': `Bearer ${MASV_API_KEY}`
  //     },
  //     body: JSON.stringify({
  //       name: "Video Analysis Package",
  //       sender: user?.email || 'default@example.com',
  //       description: "Video uploaded for analysis"
  //     }),
  //   });
  //   const { id, access_token } = await response.json();
  //   return { id, access_token };
  // }

  // const startUpload = () => {
  //   if (!file || !uploader) {
  //     console.error('No file selected or uploader not initialized');
  //     return;
  //   }
  
  //   const masvFile = {
  //     id: 'video-for-analysis',
  //     file: file,
  //     path: '',
  //   };
  
  //   uploader.addFiles(masvFile);
  // };


  // const handleFileChange = async (event) => {
  //   const selectedFile = event.target.files[0];
  //   setFile(selectedFile);
    
  //   if (selectedFile) {
  //     try {
  //       const portalID = await fetchPortalID(portalSubdomain);
  //       const { id, access_token } = await createPackage(portalID);
        
  //       const newUploader = new Uploader(id, access_token, 'https://api.massive.app');
  //       setUploader(newUploader);
  
  //       newUploader.on(Uploader.UploaderEvents.Progress, (event) => {
  //         const progress = event.data.progress;
  //         console.log(`Upload progress: ${progress}%`);
  //         setUploadProgress(progress);
  //       });
  
  //       newUploader.on(Uploader.UploaderEvents.Finished, async (event) => {
  //         console.log('Upload finished');
  //         setUploadProgress(100);
  //         await handleAnalysis(id);
  //       });
  
  //       newUploader.on(Uploader.UploaderEvents.Error, (error) => {
  //         console.error('Upload error:', error);
  //         // Handle error (e.g., show error message to user)
  //       });
  
  //     } catch (error) {
  //       console.error('Error setting up upload:', error);
  //       // Handle error (e.g., show error message to user)
  //     }
  //   }
  // };
  
  // const handleAnalysis = async (packageId) => {
  //   try {
  //     // Notify your backend about the completed upload and trigger analysis
  //     const response = await fetch('http://localhost:5000/process-video', {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json',
  //       },
  //       body: JSON.stringify({ package_id: packageId }),
  //     });
  //     const data = await response.json();
  //     setVideoId(data.video_id);
  //     setAnalysis(data.analysis);
  //   } catch (error) {
  //     console.error('Error during analysis:', error);
  //     // Handle error (e.g., show error message to user)
  //   }
  // };

  // /***************************End of MASV***************************/

            /* <div className="mb-4">
            {console.log("Printing the input button.")}
            <input type="file" onChange={handleFileChange} accept="video/*" className="mb-2" />
            <button 
              onClick={startUpload} 
              className="bg-blue-500 text-white px-4 py-2 rounded"
              disabled={!file || !uploader}
            >
              Upload and Analyze
            </button>
          </div>

          {uploadProgress > 0 && uploadProgress < 100 && (
            <div className="mb-4">
              {console.log("Entered upload progress.")}
              <progress value={uploadProgress} max="100"></progress>
              <p>{uploadProgress}% uploaded</p>
            </div>
          )} */