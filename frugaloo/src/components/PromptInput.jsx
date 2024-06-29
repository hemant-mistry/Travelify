import React, { useRef, useEffect } from "react";
import sendIcon from "../assets/sendicon.png"; // Adjust the path based on your folder structure
import attachmentIcon from "../assets/attachmenticon.png";
function PromptInput() {
  const textareaRef = useRef(null);

  const adjustHeight = () => {
    const textarea = textareaRef.current;
    textarea.style.height = "auto"; // Reset height to auto to calculate scrollHeight correctly
    textarea.style.height = `${textarea.scrollHeight}px`;
  };

  useEffect(() => {
    adjustHeight(); // Adjust height on initial render
  }, []);

  return (
    <div className="fixed bottom-0 w-full p-4 flex items-end">
      <div className="relative flex"></div>
      <button className="btn btn-square mr-2">
      <img src={attachmentIcon} alt="Icon" className="h-6 w-6" />
      </button>
      <textarea
        ref={textareaRef}
        placeholder="Enter your prompt here..."
        rows="1"
        className="textarea textarea-bordered w-full max-h-44 max-w-100 resize-none overflow-auto"
        onInput={adjustHeight}
      ></textarea>
      <button className="btn btn-square ml-2">
      <img src={sendIcon} alt="Icon" className="h-6 w-6" />
      </button>
    </div>
  );
}

export default PromptInput;
