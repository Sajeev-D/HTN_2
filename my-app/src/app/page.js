'use client';

import React from 'react';
import { useUser } from '@auth0/nextjs-auth0/client';
import Dashboard from './components/Dashboard';

export default function Index() {
  const { user, error, isLoading } = useUser();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>{error.message}</div>;
  
  if (user) {
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

    return (
      <div>
        <Dashboard />
      </div>
    );
  }

  return <a href="/api/auth/login">Login</a>;
}