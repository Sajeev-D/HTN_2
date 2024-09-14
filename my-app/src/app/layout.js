import React from 'react';
import { UserProvider } from '@auth0/nextjs-auth0/client';

export default function App({ children }) {
  return (
    <html lang="en">
      <head>
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <link
          rel="shortcut icon mask-icon"
          href="https://cdn.auth0.com/website/auth0_favicon.svg"
          color="#000000"
        />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin=""
        />
        <link
          href="https://fonts.googleapis.com/icon?family=Material+Icons"
          rel="stylesheet"
        />
      </head>
      <UserProvider>
        <body>{children}</body>
      </UserProvider>
    </html>
  );
}
