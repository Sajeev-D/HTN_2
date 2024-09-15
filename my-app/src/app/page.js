'use client';

import React from 'react';
import { useUser } from '@auth0/nextjs-auth0/client';
import Dashboard from './components/Dashboard';

export default function Index() {
  const { user, error, isLoading } = useUser();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>{error.message}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Video Analysis Tool</h1>
      {user ? (
        <Dashboard />
      ) : (
        <a href="/api/auth/login" className="bg-blue-500 text-white px-4 py-2 rounded">
          Log in
        </a>
      )}
    </div>
  );
}