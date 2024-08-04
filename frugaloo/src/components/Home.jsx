import React from "react";
import { useNavigate } from "react-router-dom";
import heroImage from "../assets/travelifyheroimage.png"; // Add your side image here
import GeminiIcon from "../assets/GeminiIcon.png";
import SupabaseTechStack from "../assets/SupabaseTechStack.png";
import googleMapIcon from "../assets/googleMapIcon.png";
import travelpic from "../assets/travelpic.png";
import dynamicchange from "../assets/dynamicchange.png";
import moneyIcon from "../assets/moneyIcon.png";
function Home() {
  const navigate = useNavigate();

  const handleGetStartedClick = () => {
    navigate("/planinput");
  };

  return (
    <>
      {/* Travelify Hero Section */}
      <div className="hero min-h-screen">
        <div className="flex flex-col md:flex-row items-center justify-between w-full pt-10 md:pt-0 md:pl-10">
          <div className="hero-content flex flex-col items-center md:items-start text-center max-w-lg md:w-1/2">
            <h1 className="mb-5 text-5xl font-bold text-white text-center md:text-left md:ml-10">
              Welcome to <br /> Travelify
            </h1>
            <p className="text-white text-center mb-5 md:text-left md:mb-5 md:ml-10">
              Travel planning just got a whole lot exciting!
            </p>
            <button
              className="flex items-center justify-center px-14 py-3 gap-2 bg-gradient-to-r from-blue-600 via-blue-700 to-blue-900 rounded-lg text-white rounded-[15px] md:self-start md:ml-10"
              onClick={handleGetStartedClick}
            >
              Get Started
            </button>
          </div>
          <div className="flex justify-center items-center w-full md:w-1/2">
            <img
              src={heroImage}
              alt="Travel Illustration"
              className="max-sm:hidden md:block md:w-[400px] lg:block"
            />
          </div>
        </div>
      </div>
      {/* Travelify Tech stack Section */}
      <div className="bg-[#3c4455]/75 w-full h-auto md:h-[132px] flex flex-col gap-5 md:flex-row justify-between items-center p-[65px]">
        <div className="flex items-center mb-4 md:mb-0">
          <img src={GeminiIcon} alt="Image 1" className="w-10 h-15 mr-2" />
          <p className="text-white text-2xl">Gemini</p>
        </div>

        <div className="flex items-center mb-4 md:mb-0">
          <img src={googleMapIcon} alt="Image 2" className="w-15 h-15 mr-2" />
          <p className="text-white text-2xl">Google Places API</p>
        </div>

        <div className="flex items-center mb-4 md:mb-0">
          <img
            src={SupabaseTechStack}
            alt="Image 3"
            className="w-15 h-15 mr-2"
          />
          <p className="text-white text-2xl">Supabase</p>
        </div>

        <div className="flex items-center">
          <p className="text-white text-2xl">ReactJS + Django</p>
        </div>
      </div>
      <br />
      <br />
      <br />
      {/* Travelify features description section */}
      <div className="flex flex-col items-center justify-center">
        <div className="text-4xl">Features of Travelify</div>
        <div className="w-[22rem] text-sm text-center md:text-md md:w-[50rem] md:p-5 mt-2">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut sed
          viverra faucibus ac imperdiet pellentesque. Sit purus augue arcu quam
          orci. Et tortor, gravida libero et amet. Pretium commodo, odio viverra
          mauris vitae sisl congue bibendume. Lorem scelerisque volutpat aliquam
          convallis tellus nunc, molestie.
        </div>
      </div>
      <div className="flex flex-col md:flex-row gap-10 items-center justify-center mt-10 font-lato">
        <div className="card card-compact bg-[#202020] w-[348px] h-[375px] shadow-xl">
          <figure className="mb-5 mt-[4rem]">
            <img src={travelpic} alt="Build Itinerary" />
          </figure>
          <div className="card-body flex flex-col items-center justify-center">
            <h2 className="card-title text-center">Itinerary Builder</h2>
            <p className="text-center w-[200px] text-custom-gray">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut sed
              viverra faucibus ac imperdiet pellentesque. Sit purus augue arcu
              quam orci. Et tortor, gravida libero et amet. Pretium commodo,
              odio viverra
            </p>
          </div>
        </div>
        <div className="card card-compact bg-[#202020] w-[348px] h-[375px] shadow-xl">
          <figure className="mb-5 mt-[4rem]">
            <img src={dynamicchange} alt="Dynamic Switch" />
          </figure>
          <div className="card-body flex flex-col items-center justify-center">
            <h2 className="card-title text-center">Dynamic Switch</h2>
            <p className="text-center w-[200px] text-custom-gray">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut sed
              viverra faucibus ac imperdiet pellentesque. Sit purus augue arcu
              quam orci. Et tortor, gravida libero et amet. Pretium commodo,
              odio viverra
            </p>
          </div>
        </div>
        <div className="card card-compact bg-[#202020] w-[348px] h-[375px] shadow-xl">
          <figure className="mb-5 mt-[4rem]">
            <img src={moneyIcon} alt="Finance AI" />
          </figure>
          <div className="card-body flex flex-col items-center justify-center">
            <h2 className="card-title text-center">Finance AI</h2>
            <p className="text-center w-[200px] text-custom-gray">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut sed
              viverra faucibus ac imperdiet pellentesque. Sit purus augue arcu
              quam orci. Et tortor, gravida libero et amet. Pretium commodo,
              odio viverra
            </p>
          </div>
        </div>
      </div>

      <br />
      <br />
      <br />
      {/* Travelify Quick Guide section */}
      <div className="px-4 sm:px-6 lg:px-8">
  <div className="text-center text-3xl sm:text-4xl lg:text-5xl">Quick Start Guide</div>
  <ul className="timeline timeline-vertical mt-6 sm:mt-8 lg:mt-10">
    <li>
      <div className="timeline-start text-xl sm:text-2xl lg:text-3xl font-lato mr-3 sm:mr-4 lg:mr-5">
        Login Or Create your account
      </div>
      <div className="timeline-middle">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className="h-4 w-4 sm:h-5 sm:w-5"
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
            clipRule="evenodd"
          />
        </svg>
      </div>
      <div className="timeline-end font-lato p-4 sm:p-5 text-custom-gray w-full sm:w-[400px] lg:w-[450px]">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. At sit ut nulla eu stetur eget. Nec, ac, sollicitudin aliquam ut egestas duis dolor. Congue suspendisse aliquam ut egestas duis dolor. Congue suspendisse consectetur adipiscing elit. At sit ut nulla eu stetur eget. Nec, ac, sollicitudin aliquam ut egestas duis dolor. Congue suspendisse aliquam ut egestas duis dolor. Congue suspendiss consectetur adipiscing elit.
      </div>
      <hr className="bg-[#40A9EB] w-full sm:w-1/2 lg:w-1/3 mx-auto"/>
    </li>
    
    <li>
      <hr className="bg-[#40A9EB] w-full sm:w-1/2 lg:w-1/3 mx-auto"/>
      <div className="timeline-start text-xl sm:text-2xl lg:text-3xl font-lato mr-3 sm:mr-4 lg:mr-5">Click on Get Started</div>
      <div className="timeline-middle">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className="h-4 w-4 sm:h-5 sm:w-5"
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
            clipRule="evenodd"
          />
        </svg>
      </div>
      <div className="timeline-end font-lato p-4 sm:p-5 text-custom-gray w-full sm:w-[400px] lg:w-[450px]">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. At sit ut nulla eu stetur eget. Nec, ac, sollicitudin aliquam ut egestas duis dolor. Congue suspendisse aliquam ut egestas duis dolor.
      </div>
      <hr className="bg-[#40A9EB] w-full sm:w-1/2 lg:w-1/3 mx-auto"/>
    </li>
    <li>
      <hr className="bg-[#40A9EB] w-full sm:w-1/2 lg:w-1/3 mx-auto"/>
      <div className="timeline-start text-xl sm:text-2xl lg:text-3xl font-lato mr-3 sm:mr-4 lg:mr-5">Enter your plan details</div>
      <div className="timeline-middle">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className="h-4 w-4 sm:h-5 sm:w-5"
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
            clipRule="evenodd"
          />
        </svg>
      </div>
      <div className="timeline-end font-lato p-4 sm:p-5 text-custom-gray w-full sm:w-[400px] lg:w-[450px]">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. At sit ut nulla eu stetur eget. Nec, ac, sollicitudin aliquam ut egestas duis dolor. r adipiscing elit. At sit ut nulla eu stetur eget. Nec, ac, sollicitudin aliquam ut egestas duis dolor. Congue suspendisse aliquam ut egestas duis dolor. Congue suspendiss consectetur adipiscing elit.
      </div>
      <hr className="bg-[#40A9EB] w-full sm:w-1/2 lg:w-1/3 mx-auto"/>
    </li>
    <li>
      <hr className="bg-[#40A9EB] w-full sm:w-1/2 lg:w-1/3 mx-auto"/>
      <div className="timeline-start text-xl sm:text-2xl lg:text-3xl font-lato mr-3 sm:mr-4 lg:mr-5">Build Itinerary</div>
      <div className="timeline-middle">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className="h-4 w-4 sm:h-5 sm:w-5"
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
            clipRule="evenodd"
          />
        </svg>
      </div>
      <div className="timeline-end font-lato p-4 sm:p-5 text-custom-gray w-full sm:w-[400px] lg:w-[450px]">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. At sit ut nulla eu stetur eget. Nec, ac, sollicitudin aliquam ut egestas duis dolor. r adipiscing elit. At sit ut nulla eu stetur eget. Nec, ac, sollicitudin aliquam ut egestas duis dolor. Congue suspendisse aliquam ut egestas duis dolor. Congue suspendiss consectetur adipiscing elit.
      </div>
      <hr className="bg-[#40A9EB] w-full sm:w-1/2 lg:w-1/3 mx-auto"/>
    </li>
  </ul>
</div>

      <br />
      <br />
      <br />
      <footer className="footer footer-center bg-base-300 text-base-content p-4">
  <aside>
    <p>Copyright © {new Date().getFullYear()} - All right reserved by Travelify</p>
  </aside>
</footer>
    </>
  );
}

export default Home;
