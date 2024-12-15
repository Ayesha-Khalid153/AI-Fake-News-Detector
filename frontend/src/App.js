<<<<<<< HEAD
import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

function App() {
  const [text, setText] = useState(""); // State to manage textarea content
  const [isDetected, setIsDetected] = useState(false); // State to track detection
  const [isVisible, setIsVisible] = useState(false); // State to toggle the new button
  const [data, setData] = useState([]); // State to store data fetched from backend
  const [loading, setLoading] = useState(true); // State to handle loading status
  const [error, setError] = useState(null); // State to handle errors from the backend
  const [postResponse, setPostResponse] = useState(""); // State to store POST response from backend

  // Fetch data from the backend (GET request)
  useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/api/data") // Adjust with your backend URL if needed
      .then((response) => {
        setData(response.data); // Store the fetched data
        setLoading(false); // Set loading to false once data is fetched
      })
      .catch((err) => {
        setError("Failed to fetch data");
        setLoading(false);
      });
  }, []); // Empty dependency array to fetch data only once when the component mounts

  // Handle detection button click
  const handleDetect = () => {
    setIsDetected(true); // Show "Detected" message
    setIsVisible(true); // Show the "True" button
    // Send the text input to backend for processing (POST request)
    axios
      .post("http://127.0.0.1:5000/api/process", { input: { key: text } })
      .then((response) => {
        console.log(response.data); // Log the response from the backend
        setPostResponse(response.data.message); // Set the response message
      })
      .catch((error) => {
        setError("Error: Could not process the data");
      });
  };

  // Handle clear button click
  const handleClear = () => {
    setText(""); // Clear the textarea content
    setIsDetected(false); // Reset "Detected" message
    setIsVisible(false); // Hide the "True" button
  };

  // Show loading state or error message if fetching data failed
  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

=======
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

>>>>>>> f03a7b484d2e65155564bac7cade53ebbcc6b96a
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-purple-200 to-blue-100 p-5">
      <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-lg">
        <h1 className="text-3xl font-bold text-center text-customBlue mb-4">
<<<<<<< HEAD
          Evaluate AI to{" "}
=======
          Evaluate AI to{' '}
>>>>>>> f03a7b484d2e65155564bac7cade53ebbcc6b96a
          <span className="text-customPurple">News Authentication</span>
        </h1>
        <textarea
          className="w-full h-40 border border-gray-300 rounded-md p-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-customBlue focus:border-transparent"
          placeholder="Type or Paste"
<<<<<<< HEAD
          value={text} // Bind value to the `text` state
=======
          value={text}            // Bind value to the `text` state
>>>>>>> f03a7b484d2e65155564bac7cade53ebbcc6b96a
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
<<<<<<< HEAD

        {/* Display the fetched data from the backend */}
        <div className="mt-6">
          <h2 className="text-xl font-semibold text-center mb-4">
            Fetched Data from Backend
          </h2>
          <ul className="space-y-2">
            {data.map((item, index) => (
              <li key={index} className="border p-2 rounded-md shadow-sm">
                {JSON.stringify(item)} {/* Display each record as JSON */}
              </li>
            ))}
          </ul>
        </div>

        {/* Display the POST request response */}
        {postResponse && (
          <div className="mt-6">
            <h2 className="text-xl font-semibold text-center mb-4">
              Server Response
            </h2>
            <p className="text-center">{postResponse}</p>
          </div>
        )}
=======
>>>>>>> f03a7b484d2e65155564bac7cade53ebbcc6b96a
      </div>
    </div>
  );
}

export default App;
