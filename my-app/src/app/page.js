'use client';

import { useUser } from '@auth0/nextjs-auth0/client';
import { useEffect } from 'react';
import Dashboard from './components/Dashboard';

export default function Index() {
  const { user, error, isLoading } = useUser();

  const styles = {
    container: {
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(to right, #4a00e0, #8e2de2)',
      color: 'white',
      fontFamily: 'Arial, sans-serif',
    },
    title: {
      fontSize: '2.5rem',
      fontWeight: 'bold',
      marginBottom: '1rem',
      textAlign: 'center',
    },
    description: {
      fontSize: '1.2rem',
      marginBottom: '2rem',
      textAlign: 'center',
      maxWidth: '400px',
    },
    button: {
      backgroundColor: 'white',
      color: '#6a11cb',
      padding: '0.75rem 2rem',
      borderRadius: '9999px',
      fontWeight: 'bold',
      textDecoration: 'none',
      transition: 'all 0.3s ease',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    },
    buttonHover: {
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      transform: 'scale(1.05)',
    },
  };

  if (isLoading) return (
    <div style={styles.container}>
      <div style={styles.title}>Loading...</div>
    </div>
  );

  if (error) return (
    <div style={styles.container}>
      <div style={styles.description}>{error.message}</div>
    </div>
  );

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

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Welcome to Our App</h1>
      <p style={styles.description}>Securely log in to access your personalized dashboard and start your journey.</p>
      <a 
        href="/api/auth/login"
        style={styles.button}
        onMouseEnter={(e) => {
          e.target.style.backgroundColor = styles.buttonHover.backgroundColor;
          e.target.style.transform = styles.buttonHover.transform;
        }}
        onMouseLeave={(e) => {
          e.target.style.backgroundColor = styles.button.backgroundColor;
          e.target.style.transform = 'scale(1)';
        }}
      >
        Login
      </a>
    </div>
  );
}
