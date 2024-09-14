'use client';

import { useState } from 'react';

export default function Home() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setIsLoading(true);
    setError('');
    setAnalysis('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Analysis failed');
      }

      setAnalysis(data.result);
    } catch (error) {
      console.error('Error:', error);
      setError(`An error occurred during analysis: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Video Analysis</h1>
      <form onSubmit={handleSubmit} className="mb-4">
        <input
          type="file"
          accept="video/*"
          onChange={handleFileChange}
          className="mb-2 block"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400"
        >
          {isLoading ? 'Analyzing...' : 'Analyze Video'}
        </button>
      </form>
      {error && <p className="text-red-500 mb-4">{error}</p>}
      {analysis && (
        <div>
          <h2 className="text-xl font-semibold mb-2">Analysis Result:</h2>
          <pre className="bg-gray-100 p-4 rounded whitespace-pre-wrap">
            {analysis}
          </pre>
        </div>
      )}
    </div>
  );
}


/*
Web upload section:

npm install @masvio/uploader
js-uploader
need to take html input the add files to the uploader
Can set up the cloud storage
In the new portal setting, 
the lightning challenge

*/
