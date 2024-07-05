import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import Home from "./components/Home";
import Navbar from "./components/Navbar";
import Login from "./components/Login";
import SignUp from "./components/SignUp";
import PlanInput from './components/PlanInput';
import Plan from './components/Plan';

const supabase = createClient('https://wqbvxqxuiwhmretkcjaw.supabase.co', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndxYnZ4cXh1aXdobXJldGtjamF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTk3MTYyMTQsImV4cCI6MjAzNTI5MjIxNH0.CXyPAdKKgwjmPee0OmvV4BxnQUj_4y3ARbaEuSToz6s')

function App() {
  const [session, setSession] = useState(null);
  const [loggedInUser, setLoggedInUser] = useState(null);
  useEffect(() => {
    supabase.auth.getSession().then(async ({ data: { session } }) => {
      setSession(session);
      const { data: { user } } = await supabase.auth.getUser()
      setLoggedInUser(user)
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
        <Navbar loggedInUser = {loggedInUser}/>
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
