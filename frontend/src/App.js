import React, { useState } from 'react';
import './App.css';

function App() {
  const [text, setText] = useState(''); // State to manage the textarea content
  const [isDetected, setIsDetected] = useState(false); // State to track detection
  const [isVisible, setIsVisible] = useState(false);  // State to toggle the new button

  const handleDetect = () => {
    setIsDetected(true);  // Show "Detected" message
    setIsVisible(true);   // Show the "True" button
  };

  const handleClear = () => {
    setText('');          // Clear the textarea content
    setIsDetected(false); // Reset "Detected" message
    setIsVisible(false);  // Hide the "True" button
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-purple-200 to-blue-100 p-5">
      <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-lg">
        <h1 className="text-3xl font-bold text-center text-customBlue mb-4">
          Evaluate AI to{' '}
          <span className="text-customPurple">News Authentication</span>
        </h1>
        <textarea
          className="w-full h-40 border border-gray-300 rounded-md p-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-customBlue focus:border-transparent"
          placeholder="Type or Paste"
          value={text}            // Bind value to the `text` state
          onChange={(e) => setText(e.target.value)} // Update the state on change
        />
        <div className="flex justify-center mt-4 gap-4">
          <button
            onClick={handleDetect} // Detect button click event
            className="bg-customBlue text-white px-4 py-2 rounded-md hover:bg-blue-600 transition"
          >
            Detect
          </button>
          <button
            onClick={handleClear} // Clear button click event
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 transition"
          >
            Clear
          </button>
        </div>

        {isDetected && (
          <p className="text-green-600 font-semibold mt-4 text-center">
            Detected!
          </p>
        )}

        {isVisible && (
          <div className="flex justify-center mt-4">
            <button className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 transition">
              True
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
