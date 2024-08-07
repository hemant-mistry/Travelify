import React, { useRef, useEffect, useState } from "react";
import sendIcon from "../assets/sendicon.png"; // Adjust the path based on your folder structure
import attachmentIcon from "../assets/attachmenticon.png";

function PromptInput({ onSendMessage, setLoading }) {
  const textareaRef = useRef(null);
  const [message, setMessage] = useState("");

  const adjustHeight = () => {
    const textarea = textareaRef.current;
    textarea.style.height = "auto"; // Reset height to auto to calculate scrollHeight correctly
    textarea.style.height = `${textarea.scrollHeight}px`;
  };

  useEffect(() => {
    adjustHeight(); // Adjust height on initial render
  }, []);

  const handleSendMessage = () => {
    if (message.trim() === "") {
      return; // Do not proceed if message is empty
    }

    // Pass user message to parent component
    onSendMessage(message);

    // Clear the textarea and reset height
    setMessage("");
    textareaRef.current.style.height = "auto";
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Prevent default behavior (new line)
      handleSendMessage(); // Call sendMessage function
    }
  };

  return (
    <div className="fixed bottom-0 w-full p-4 flex flex-col items-center">
      <div className="relative flex w-full justify-center mb-4 flex items-end">
        <button className="btn btn-square mr-2">
          <img src={attachmentIcon} alt="Attachment Icon" className="h-6 w-6" />
        </button>
        <textarea
          ref={textareaRef}
          placeholder="Enter your prompt here..."
          rows="1"
          className="textarea textarea-bordered w-1/2 max-h-44 resize-none overflow-auto"
          onInput={adjustHeight}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyPress} // Added key down event handler
        ></textarea>
        <button className="btn btn-square ml-2" onClick={handleSendMessage}>
          <img src={sendIcon} alt="Send Icon" className="h-6 w-6" />
        </button>
      </div>
      <div className="prompt-caution text-center text-xs">
        Gemini may display inaccurate info, including about people, so double-check its responses.{" "}
        <a className="link link-primary" href="https://support.google.com/gemini?p=privacy_notice">
          Your privacy and Gemini Apps
        </a>
      </div>
    </div>
  );
}

export default PromptInput;
