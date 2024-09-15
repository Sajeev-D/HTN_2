import React from 'react';
import { UserProvider } from '@auth0/nextjs-auth0/client';
import { Inter } from 'next/font/google';
import './globals.css';

// Initialize the Inter font
const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Your App Name',
  description: 'Description of your app',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.className}>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link
          rel="shortcut icon mask-icon"
          href="https://cdn.auth0.com/website/auth0_favicon.svg"
          color="#000000"
        />
        <link
          href="https://fonts.googleapis.com/icon?family=Material+Icons"
          rel="stylesheet"
        />
            </head>
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        <UserProvider>
          {children}
        </UserProvider>
      </body>
    </html>
  );
}