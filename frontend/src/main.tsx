import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

// Basic global styles
const style = document.createElement('style');
style.textContent = `
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  
  button:hover:not(:disabled) {
    opacity: 0.9;
  }
  
  button:active:not(:disabled) {
    transform: scale(0.98);
  }
`;
document.head.appendChild(style);

createRoot(document.getElementById('root')!).render(<App />)

