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

  const adjustHeight = () => {
    const textarea = textareaRef.current;
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  };

  useEffect(() => {
    adjustHeight();
  }, []);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (message.trim() === "") {
      return;
    }

    setIsFirstMessage(false);
    setLoading(true);

    setMessages((prevMessages) => [
      ...prevMessages,
      { type: "user", text: message.trim() },
      { type: "response", text: "" },
    ]);

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}generate-message/`,
        {
          user_id: loggedInUser.id,
          message: message.trim(),
        }
      );
      console.log("Responseeee",response);
      const { visual_response, sql_response, query_result, react_component, insights } =
        response.data;
      const cleanedVisualResponse = visual_response.trim();
      console.log("react component", react_component);
      console.log("visual_response", visual_response);
      console.log("results", query_result);
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
            insights
          };
        }
        return updatedMessages;
      });
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setLoading(false);
    }

    setMessage("");
    textareaRef.current.style.height = "auto";
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const button1Text =
    "Suggest European cities for history, nightlife, and nature.";
  const button2Text =
    "Plan a $2000 week-long Japan trip, including flights, stay, food, and activities.";
  const button3Text =
    "Create a 10-day Southeast Asia itinerary for Thailand, Vietnam, and Cambodia.";
  const button4Text =
    "What should I pack for a two-week trip to New Zealand in November?";

  const truncateText = (text, maxLength) => {
    return text.length > maxLength
      ? text.substring(0, maxLength) + "..."
      : text;
  };
  console.log(messages);
  return (
    <>
      {isFirstMessage ? (
        <div className="hero mt-10">
          <div className="hero-content text-center">
            <div className="lg:max-w-2xl sm:max-w-lg mx-auto">
              <h1 className="lg:text-5xl sm:text-5xl font-bold">
                Welcome Back, John
              </h1>
              <p className="py-6 lg:text-lg sm:text-lg">
                Provident cupiditate voluptatem et in. Quaerat fugiat ut
                assumenda excepturi exercitationem quasi. In deleniti eaque aut
                repudiandae et a id nisi.
              </p>
              <div className="suggested-prompts flex justify-center gap-4 flex-wrap">
                <button className="btn btn-primary btn-outline btn-xs sm:btn-sm md:btn-md lg:btn-md">
                  {truncateText(button1Text, 60)}
                </button>
                <button className="btn btn-primary btn-outline btn-xs sm:btn-sm md:btn-md lg:btn-md">
                  {truncateText(button2Text, 60)}
                </button>
                <button className="btn btn-primary btn-outline btn-xs sm:btn-sm md:btn-md lg:btn-md">
                  {truncateText(button3Text, 60)}
                </button>
                <button className="btn btn-primary btn-outline btn-xs sm:btn-sm md:btn-md lg:btn-md">
                  {truncateText(button4Text, 60)}
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col h-50 justify-center items-center">
          <div className="overflow-y-auto text-sm w-[100vw] h-[70vh] sm:h-[40vh] sm:w-[90vw] lg:h-[65vh] lg:w-[60vw] p-4 mt-10 no-scrollbar">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex items-start justify-start space-x-4 mb-4 ${
                  msg.type === "user" ? "user-message" : "copilot-response"
                }`}
              >
                <div className="avatar">
                  <div className="w-8 rounded-full">
                    {msg.type === "user" ? (
                      <img
                        src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.jpg"
                        alt="User"
                      />
                    ) : (
                      <img src={GeminiIcon} alt="Bot" />
                    )}
                  </div>
                </div>
                <div className="max-w-2xl">
                  {msg.type === "response" && msg.text === "" ? (
                    <span className="loading loading-dots loading-md"></span>
                  ) : msg.type === "response" &&
                    msg.cleanedVisualResponse === "1" ? (
                      <>
                      <ReactMarkdown>{msg.insights}</ReactMarkdown>
                      <br/>
                    <AreaChart
                      data={msg.query_result}
                      component_code={msg.react_component}

                    />
                    </>
                  ) : msg.type === "response" &&
                    msg.cleanedVisualResponse === "2" ? (
                      <>
                      <ReactMarkdown>{msg.insights}</ReactMarkdown>
                      <br/>
                    <BarChart
                      data={msg.query_result}
                      component_code={msg.react_component}
                    />
                    </>
                  ) : msg.type === "response" &&
                    msg.cleanedVisualResponse === "3" ? (
                      <>
                      <ReactMarkdown>{msg.insights}</ReactMarkdown>
                      <br/>
                    <LineChart
                      data={msg.query_result}
                      component_code={msg.react_component}
                    />
                    </>
                  ) : msg.type === "response" &&
                    msg.cleanedVisualResponse === "4" ? (
                      <>
                      <ReactMarkdown>{msg.insights}</ReactMarkdown>
                      <br/>
                    <PieChart
                      data={msg.query_result}
                      component_code={msg.react_component}
                    />
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
      <div className="fixed bottom-0 w-full p-4 flex flex-col items-center">
        <div className="relative flex w-full justify-center mb-4 items-end">
          <button className="btn btn-square mr-2">
            <img
              src={attachmentIcon}
              alt="Attachment Icon"
              className="h-6 w-6"
            />
          </button>
          <textarea
            ref={textareaRef}
            placeholder="Enter your prompt here..."
            rows="1"
            className="textarea textarea-bordered w-1/2 max-h-44 resize-none overflow-auto"
            onInput={adjustHeight}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyPress}
          ></textarea>
          <button className="btn btn-square ml-2" onClick={handleSendMessage}>
            <img src={sendIcon} alt="Send Icon" className="h-6 w-6" />
          </button>
        </div>
        <div className="prompt-caution text-center text-xs">
          Gemini may display inaccurate info, including about people, so
          double-check its responses. Gemini is not a substitute for an expert.
        </div>
      </div>
    </>
  );
}

export default PromptInput;
