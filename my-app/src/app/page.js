'use client';

import { useUser } from '@auth0/nextjs-auth0/client';
import { useEffect } from 'react';
import Dashboard from './components/Dashboard';
import Image from 'next/image';
import SurveillancePage from './components/Dashboard';

// Import Poppins font
import { Poppins } from 'next/font/google';

// Initialize the font
const poppins = Poppins({
  weight: ['400', '700'],
  subsets: ['latin'],
  display: 'swap',
});

export default function Index() {
  const { user, error, isLoading } = useUser();

  useEffect(() => {
    if (user) {
      console.log(user.email);
      // Send the user data to the backend
      fetch('http://localhost:5000/api/save-user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: user.email }),
      })
        .then((response) => response.json())
        .then((data) => console.log('User saved:', data))
        .catch((error) => console.error('Error saving user:', error));
    }
  }, [user]);

  if (isLoading) return <div className={`flex justify-center items-center h-screen text-2xl font-bold ${poppins.className}`}>Loading...</div>;

  if (error) return <div className={`flex justify-center items-center h-screen text-xl text-red-600 ${poppins.className}`}>{error.message}</div>;

  if (user) {
    return (
      <div className={`w-full h-screen ${poppins.className}`}>
        <SurveillancePage />
      </div>
    );
  }

  return (
    <div className={`min-h-screen w-full bg-white text-black ${poppins.className} relative overflow-hidden`}>
      {/* Content */}
      <main className="relative z-10 min-h-screen flex items-center justify-center p-8">
        <div className="max-w-6xl w-full flex flex-col md:flex-row items-center justify-between">
          <div className="w-full md:w-1/2 mb-8 md:mb-0 order-2 md:order-1">
            <Image
              src="/Surv.png"
              alt="Website Icon"
              width={800}
              height={600}
              className="mx-auto md:mx-0"
            />
          </div>
          <div className="w-full md:w-1/2 md:pr-8 text-center md:text-left order-1 md:order-2">
            <h1 className="text-4xl md:text-5xl font-bold mb-4 text-black">Survo</h1>
            <p className="text-xl text-gray-700 mb-8">The first video LLM made to augment security surveillance</p>
            <div className="space-y-4 md:space-y-0 md:space-x-4 flex flex-col md:flex-row items-center justify-center md:justify-start">
              <a href="/api/auth/login" className="w-full md:w-auto bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-full transition duration-300 transform hover:scale-105">
                Login Or Sign Up
              </a>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}