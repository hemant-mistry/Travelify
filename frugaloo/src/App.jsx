import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState, useEffect } from "react";
import { createClient } from "@supabase/supabase-js";
import Home from "./components/Home";
import Navbar from "./components/Navbar";
import Login from "./components/Login";
import SignUp from "./components/SignUp";
import PlanInput from "./components/PlanInput";
import Plan from "./components/Plan";
import PromptInput from "./components/PromptInput";
import Trip from "./components/Trips";
import Finance from "./components/Finance";
import Locate from "./components/Locate";
import HeroImage from "./assets/FrameBackground.png"; // Import the background image

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_CLIENT,
  import.meta.env.VITE_SUPABASE_SECRET
);

function App() {
  const [session, setSession] = useState(null);
  const [loggedInUser, setLoggedInUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedDayData, setSelectedDayData] = useState(null);
  const [budget, setBudget] = useState(2);
  const [imageLoaded, setImageLoaded] = useState(false); // State to track image loading

  useEffect(() => {
    async function fetchSession() {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      setSession(session);
      if (session) {
        const {
          data: { user },
        } = await supabase.auth.getUser();
        setLoggedInUser(user);
      }
      setLoading(false);
    }

    fetchSession();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    const img = new Image();
    img.src = HeroImage;
    img.onload = () => {
      setImageLoaded(true); // Set imageLoaded to true when the image is fully loaded
    };
  }, []);

  if (loading || !imageLoaded) { // Display loading spinner until both session and image are loaded
    return (
      <div className="flex justify-center items-center pt-[300px] font-lato">
        <span className="loading loading-spinner loading-lg mr-5 text-custom-blue"></span>
        Loading Travelify..
      </div>
    );
  }

  if (!session) {
    return <Login />;
  }

  return (
    <BrowserRouter>
      <div
        className="min-h-screen bg-cover bg-center"
        style={{
          backgroundImage: `url(${HeroImage})`, // Apply background image only after it's loaded
        }}
      >
        <Navbar loggedInUser={loggedInUser} />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route
            path="/planinput"
            element={
              <PlanInput
                loggedInUser={loggedInUser}
                budget={budget}
                setBudget={setBudget}
              />
            }
          />
          <Route
            path="/plan/:tripId"
            element={
              <Plan
                loggedInUser={loggedInUser}
                budget={budget}
                onLocateClick={setSelectedDayData}
              />
            }
          />
          <Route
            path="/myfinances"
            element={<PromptInput loggedInUser={loggedInUser} />}
          />
          <Route
            path="/mytrips"
            element={<Trip loggedInUser={loggedInUser} />}
          />
          <Route
            path="/Faqs"
            element={<Finance loggedInUser={loggedInUser} />}
          />
          <Route
            path="/locate/:tripId/:dayId"
            element={<Locate loggedInUser={loggedInUser} dayData={selectedDayData} />}
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
