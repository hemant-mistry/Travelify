import React from "react";
import { useNavigate } from "react-router-dom";
import HeroImage from "../assets/NYC.png";
import TravelIcon from "../assets/TravelIcon.png";
function Home() {
  const navigate = useNavigate();

  const handleGetStartedClick = () => {
    navigate("/planinput");
  };

  return (
    <>
      <div
        className="hero min-h-screen fixed"
        style={{
          backgroundImage: `url(${HeroImage})`,
        }}
      >
        <div
          className="hero-overlay"
          style={{ backgroundColor: "rgba(0, 0, 0, 0.80)" }} // Adjust opacity as needed
        ></div>
        <div
          className="hero-content text-center"
          style={{ marginTop: "-10rem" }}
        >
          <div className="max-w-lg">
            <h1 className="mb-5 text-5xl font-bold text-white">
              Welcome to Travelify
            </h1>
            <p className="mb-10 text-white">
              Provident cupiditate voluptatem et in. Quaerat fugiat ut assumenda
              excepturi exercitationem quasi. In deleniti eaque aut repudiandae
              et a.
            </p>
            <div className="flex justify-center">
              <button
                className="btn btn-primary"
                onClick={handleGetStartedClick}
              >
                <img src={TravelIcon} alt="Gemini Icon" className="h-6 w-6" />
                Get Started
              </button>
              <button
                className="btn btn-outline ml-5"
              >
                Learn more..
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default Home;
