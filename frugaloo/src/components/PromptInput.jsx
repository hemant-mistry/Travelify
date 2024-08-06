import React, { useRef, useEffect, useState } from "react";
import axios from "axios";
import sendIcon from "../assets/sendicon.png";
import attachmentIcon from "../assets/attachmenticon.png";
import GeminiIcon from "../assets/GeminiIcon.png";
import ReactMarkdown from "react-markdown";
import LineChart from "./Charts/LineChart"; // Import the LineChart component
import PieChart from "./Charts/PieChart"; // Import the PieChart component
import AreaChart from "./Charts/AreaChart";
import BarChart from "./Charts/BarChart";

function PromptInput({ loggedInUser }) {
  const textareaRef = useRef(null);
  const messagesEndRef = useRef(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [isFirstMessage, setIsFirstMessage] = useState(true);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  useEffect(() => {
    adjustHeight();
  }, [message]);

  useEffect(() => {
    // Clear chat history on component mount
    sessionStorage.removeItem("chat_history");
  }, []);

  const initializeChatHistory = () => {
    const chatHistory = JSON.parse(sessionStorage.getItem("chat_history")) || {
      contents: [
        { role: "user", parts: [] },
        { role: "model", parts: [] },
      ],
    };
    sessionStorage.setItem("chat_history", JSON.stringify(chatHistory));
  };
  const updateChatHistory = (message, role) => {
    // Get the current chat history or initialize an empty array
    const chatHistory = JSON.parse(sessionStorage.getItem("chat_history")) || {
      contents: [
        { role: "user", parts: [] },
        { role: "model", parts: [] },
      ],
    };

    console.log("Before Update:", chatHistory);

    // Add the new message to the appropriate role
    const roleIndex = chatHistory.contents.findIndex(
      (entry) => entry.role === role
    );

    if (roleIndex !== -1) {
      chatHistory.contents[roleIndex].parts.push({ text: message });
    }

    console.log("After Update:", chatHistory);

    sessionStorage.setItem("chat_history", JSON.stringify(chatHistory));
  };
  const handleSendMessage = async () => {
    if (message.trim() === "" && !isFirstMessage) {
      return;
    }

    setIsFirstMessage(false);
    setLoading(true);

    const newMessage = message.trim();

    setMessages((prevMessages) => [
      ...prevMessages,
      { type: "user", text: newMessage },
      { type: "response", text: "" },
    ]);

    // Save the user's message to chat history
    updateChatHistory(newMessage, "user");

    try {
      const chatHistory = isFirstMessage
        ? [] // Send an empty array if it's the first message
        : JSON.parse(sessionStorage.getItem("chat_history")) || [];

      console.log("Chat history:", chatHistory);

      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}generate-message/`,
        {
          user_id: loggedInUser.id,
          message: newMessage,
          chat_history: JSON.stringify(chatHistory), // Ensure chat history is a JSON string
        }
      );

      console.log("Response Data:", response.data);

      const {
        visual_response,
        sql_response,
        query_result,
        react_component,
        insights,
      } = response.data;

      const cleanedVisualResponse = visual_response.trim();

      setMessages((prevMessages) => {
        const updatedMessages = [...prevMessages];
        const responseIndex = updatedMessages.findIndex(
          (msg) => msg.type === "response" && msg.text === ""
        );
        if (responseIndex !== -1) {
          updatedMessages[responseIndex] = {
            type: "response",
            cleanedVisualResponse,
            sql_response,
            query_result,
            react_component,
            insights,
          };
        }
        return updatedMessages;
      });

      // Save the model's response to chat history
      updateChatHistory(response.data.insights || "", "model");
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setLoading(false);
    }

    setMessage("");
  };
  useEffect(() => {
    if (message.trim() !== "") {
      handleSendMessage();
    }
  }, [message]);
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };



  const adjustHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"; // Reset the height
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`; // Set to scrollHeight
    }
  };

  const button1Text =
    "Can you give me a comparison of my spendings for all my trips";
  const button2Text =
    "Show me the cost breakdown for my trips based on categories";
  const button3Text = "Can you show me the place where I spent the most";

  const truncateText = (text, maxLength) => {
    return text.length > maxLength
      ? text.substring(0, maxLength) + "..."
      : text;
  };
  const handleButtonClick = (buttonText) => {
    setMessage(buttonText);
  };
  return (
    <>
      {isFirstMessage ? (
        <div className="flex flex-col pt-[80px]">
          <div className="flex flex-col text-center mx-auto w-full max-w-2xl">
            <h1 className="lg:text-5xl sm:text-5xl font-bold">Welcome back!</h1>
            <p className="py-6 lg:text-lg sm:text-lg">
              Get to know how you spent on your trip with the help of Finance
              AI. <br></br>
              Select one of the prompts mentioned below to get started.
            </p>
            <div className="suggested-prompts flex justify-center gap-4 flex-wrap">
              <button
                className="btn btn-primary btn-outline btn-xs sm:btn-sm md:btn-md lg:btn-md"
                onClick={() => handleButtonClick(button1Text)}
              >
                {truncateText(button1Text, 60)}
              </button>
              <button
                className="btn btn-primary btn-outline btn-xs sm:btn-sm md:btn-md lg:btn-md "
                onClick={() => handleButtonClick(button2Text)}
              >
                {truncateText(button2Text, 60)}
              </button>
              <button
                className="btn btn-primary btn-outline btn-xs sm:btn-sm md:btn-md lg:btn-md"
                onClick={() => handleButtonClick(button3Text)}
              >
                {truncateText(button3Text, 60)}
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center pt-[80px]">
          <div className="flex flex-col overflow-y-auto text-md w-full max-w-2xl h-[70vh] sm:h-[40vh] lg:h-[65vh] p-4 no-scrollbar">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex items-start space-x-4 mb-4 ${
                  msg.type === "user" ? "justify-start" : "justify-start"
                }`}
              >
                <div className="avatar w-8 rounded-full">
                  {msg.type === "user" ? (
                    <div className="avatar placeholder">
                      <div className="bg-neutral text-neutral-content w-8 rounded-full">
                        <span className="text-sm">{loggedInUser.email[0]}</span>
                      </div>
                    </div>
                  ) : (
                    <div className="avatar">
                      <div className="w-8 rounded-full">
                        <img src={GeminiIcon} alt="Bot" />
                      </div>
                    </div>
                  )}
                </div>
                <div className="w-full flex flex-col">
                  {msg.type === "response" ? (
                    <>
                      {msg.text === "" ? (
                        <span className="loading loading-dots loading-md"></span>
                      ) : (
                        <>
                          <ReactMarkdown>{msg.insights}</ReactMarkdown>
                          <br />
                          {msg.cleanedVisualResponse === "1" &&
                            msg.react_component && (
                              <AreaChart
                                data={msg.query_result}
                                component_code={msg.react_component}
                              />
                            )}
                          {msg.cleanedVisualResponse === "2" &&
                            msg.react_component && (
                              <BarChart
                                data={msg.query_result}
                                component_code={msg.react_component}
                              />
                            )}
                          {msg.cleanedVisualResponse === "3" &&
                            msg.react_component && (
                              <LineChart
                                data={msg.query_result}
                                component_code={msg.react_component}
                              />
                            )}
                          {msg.cleanedVisualResponse === "4" &&
                            msg.react_component && (
                              <PieChart
                                data={msg.query_result}
                                component_code={msg.react_component}
                              />
                            )}
                          <br />
                        </>
                      )}
                    </>
                  ) : (
                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      <div className="fixed h-50 w-full p-2 flex flex-col items-center gap-2 ml-3 bottom-5">
        <div className="relative w-full max-w-2xl">
          <div className="flex items-center relative">
            <textarea
              ref={textareaRef}
              rows={1}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your message..."
              className="w-full rounded-lg p-2 resize-none pr-12" // Add padding-right to make space for the button
            />
            <div className="flex items-center absolute right-2 top-0 h-full">
              <button
                className="flex items-center justify-center"
                onClick={handleSendMessage}
                disabled={loading}
              >
                <img src={sendIcon} alt="Send" className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>
        <div className="prompt-caution text-center text-xs mt-2">
          Gemini may display inaccurate info, including about people, so
          double-check its responses.{" "}
          <a
            className="link link-primary"
            href="https://support.google.com/gemini?p=privacy_notice"
          >
            Your privacy and Gemini Apps
          </a>
        </div>
      </div>
    </>
  );
}

export default PromptInput;
