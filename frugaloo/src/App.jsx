import { useState } from "react";
import Navbar from "./components/Navbar";
import PromptInput from "./components/PromptInput";
import GeminiIcon from "./assets/GeminiIcon.png";

function truncateText(text, maxLength) {
  if (text.length > maxLength) {
    return text.substring(0, maxLength) + "...";
  }
  return text;
}

function App() {
  const [isFirstMessage, setIsFirstMessage] = useState(true);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false); // New state variable

  const handleSendMessage = (userMessage, responseMessage) => {
    setIsLoading(true); // Set loading state to true
    const newMessages = [];
    if (userMessage !== null) {
      newMessages.push({ type: "user", text: userMessage });
    }
    if (responseMessage !== null) {
      newMessages.push({ type: "response", text: responseMessage });
      setIsLoading(false); // Set loading state to false once response received
    }
    
    setMessages((prevMessages) => [
      ...prevMessages,
      ...newMessages,
    ]);
    
    setIsFirstMessage(false);
  };

  // Example button texts
  const button1Text =
    "Suggest European cities for history, nightlife, and nature.";
  const button2Text =
    "Plan a $2000 week-long Japan trip, including flights, stay, food, and activities.";
  const button3Text =
    "Create a 10-day Southeast Asia itinerary for Thailand, Vietnam, and Cambodia.";
  const button4Text =
    "What should I pack for a two-week trip to New Zealand in November?";

  return (
    <>
      <Navbar />
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
          <div className="overflow-y-auto w-[60vw] h-[70vh] sm:h-[40vh] sm:w-[30vw] lg:h-[65vh] lg:w-[60vw] p-4 mt-10 no-scrollbar">
            {isLoading ? (
              <div className="text-center">Loading...</div> // Display loading message
            ) : (
              messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex items-start justify-start space-x-4 mb-4 ${
                    msg.type === "user" ? "user-message" : "copilot-response"
                  }`}
                >
                  <div className="avatar">
                    <div className="w-8 rounded-full">
                      {msg.type === "user" ? (
                        <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.jpg" alt="user avatar" />
                      ) : (
                        <img src={GeminiIcon} alt="Gemini icon" />
                      )}
                    </div>
                  </div>
                  <div>{msg.text}</div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
      <PromptInput onSendMessage={handleSendMessage} />
    </>
  );
}

export default App;
