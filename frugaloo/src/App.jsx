import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from "./components/Home";
import Navbar from "./components/Navbar";
import Login from "./components/Login";
import SignUp from "./components/SignUp";  // Import SignUp component
import Plan from './components/Plan';

function App() {
  return (
    <BrowserRouter>
      <div>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/plan" element = {<Plan/>}/>
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
