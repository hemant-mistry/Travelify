import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import Home from "./components/Home";
import Navbar from "./components/Navbar";
import Login from "./components/Login";
import SignUp from "./components/SignUp";
import PlanInput from './components/PlanInput';
import Plan from './components/Plan';

const supabase = createClient('https://gudqtcrukrjdjipnavsn.supabase.co', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1ZHF0Y3J1a3JqZGppcG5hdnNuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTQxNDA3ODgsImV4cCI6MjAyOTcxNjc4OH0.wlopJVGLMcro2mRHsbFGhV0YdMa61w8w_MeA8NFB8a0')

function App() {
  const [session, setSession] = useState(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  if (!session) {
    return <Login />;
  }

  return (
    <BrowserRouter>
      <div>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/planinput" element={<PlanInput />} />
          <Route path="/plan" element={<Plan />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
