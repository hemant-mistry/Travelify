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
  "https://wqbvxqxuiwhmretkcjaw.supabase.co",
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndxYnZ4cXh1aXdobXJldGtjamF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTk3MTYyMTQsImV4cCI6MjAzNTI5MjIxNH0.CXyPAdKKgwjmPee0OmvV4BxnQUj_4y3ARbaEuSToz6s"
);

function App() {
  const [session, setSession] = useState(null);
  const [loggedInUser, setLoggedInUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedDayData, setSelectedDayData] = useState(null);
  const [budget, setBudget] = useState(2);

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

  if (loading) {
    return (
      <div className="flex justify-center items-center mt-[300px] text-primary">
        <span className="loading loading-spinner loading-lg mr-5"></span>
        Loading Travelify...
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
          backgroundImage: `url(${HeroImage})`, // Apply background image
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
            path="/PromptInput"
            element={<PromptInput loggedInUser={loggedInUser} />}
          />
          <Route path="/mytrips" element={<Trip loggedInUser={loggedInUser} />} />
          <Route
            path="/myfinances"
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
