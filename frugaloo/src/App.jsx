import { useState } from "react";
import Navbar from "./components/Navbar";
import PromptInput from "./components/PromptInput";

function truncateText(text, maxLength) {
  if (text.length > maxLength) {
    return text.substring(0, maxLength) + "...";
  }
  return text;
}

function App() {
  const [isFirstMessage, setIsFirstMessage] = useState(true);
  
  // Example button texts
  const button1Text = "Suggest European cities for history, nightlife, and nature.";
  const button2Text = "Plan a $2000 week-long Japan trip, including flights, stay, food, and activities.";
  const button3Text = "Create a 10-day Southeast Asia itinerary for Thailand, Vietnam, and Cambodia.";
  const button4Text = "What should I pack for a two-week trip to New Zealand in November?";

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
        <div className="flex flex-col h-full">
          <div className="overflow-y-auto h-[70vh] sm:h-[40vh] lg:h-[75vh] pl-4 pr-4">
            <div className="chat chat-end mx-4 mt-5">
              <div className="chat-bubble p-4 rounded-lg mb-2">
                You underestimate my power!
              </div>
            </div>
            <div className="chat chat-start mt-5 mx-4">
              <div className="chat-bubble p-4 rounded-lg mb-2">
                {/* Your long content here */}
                <div className="welcome-message">
                  <p>Welcome back, John</p>
                  <br />
                  Where are you planning to go?
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      <PromptInput />
    </>
  );
}

export default App;
