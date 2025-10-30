import React from 'react';
import ReactDOM from 'react-dom/client';
// Ensure PlaySmart.jsx is in the same 'src' directory
import PlaySmart from './PlaySmart.jsx';
// Ensure index.css is in the same 'src' directory
import './index.css';

// Rendering the main application component into the HTML root element
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <PlaySmart />
  </React.StrictMode>,
);
