import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createClient } from "@supabase/supabase-js";
import helpicon from "../assets/helpicon.png";
import loginIcon from "../assets/loginIcon.png";
import VideoWalkThrough from "../assets/VideoWalkThroughIcon.png";
import addIcon from "../assets/addIcon.png";
import { useNavigate } from "react-router-dom";

const supabase = createClient(
  "https://wqbvxqxuiwhmretkcjaw.supabase.co",
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndxYnZ4cXh1aXdobXJldGtjamF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTk3MTYyMTQsImV4cCI6MjAzNTI5MjIxNH0.CXyPAdKKgwjmPee0OmvV4BxnQUj_4y3ARbaEuSToz6s"
);

function Navbar({ loggedInUser }) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();

  const handleAvatarClick = () => {
    setDropdownOpen(!dropdownOpen);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    window.location.reload();
  };

  const handleAddIconClick = () => {
    navigate("/planinput");
  };

  const handleHelpClick = () => {
    navigate("/Faqs");
  };

  const handleScroll = () => {
    if (window.scrollY > 0) {
      setScrolled(true);
    } else {
      setScrolled(false);
    }
  };

  useEffect(() => {
    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  return (
    <>
      <div
        className={`navbar rounded-md fixed w-full transition-all duration-300 ease-in-out ${
          scrolled ? 'bg-black z-50' : 'z-50'
        }`}
      >
        <div className="flex-1">
          <Link to="/" className="btn btn-ghost text-xl">
            Travelify
          </Link>
        </div>
        <div className="flex-none">
          <div className="help tooltip tooltip-bottom" data-tip="Add Itinerary">
            <button className="btn btn-ghost" onClick={handleAddIconClick}>
              <img src={addIcon} alt="Add Icon" className="h-6 w-6" />
            </button>
          </div>
          <div className="help tooltip tooltip-bottom" data-tip="Help">
            <button className="btn btn-ghost" onClick={handleHelpClick}>
              <img src={helpicon} alt="Help Icon" className="h-6 w-6" />
            </button>
          </div>
          <div
            className="video-walkthrough tooltip tooltip-bottom"
            data-tip="Video Walkthrough"
          >
            <button
              className="btn btn-ghost mr-2"
              onClick={() => document.getElementById("my_modal_4").showModal()}
            >
              <img src={VideoWalkThrough} alt="Video Walkthrough" className="h-6 w-6" />
            </button>
          </div>

          {!loggedInUser && (
            <Link to="/login" className="btn btn-ghost btn-md">
              <img src={loginIcon} alt="Login Icon" className="h-6 w-6" />
              Login/SignUp
            </Link>
          )}
          {loggedInUser && (
            <div
              className="video-walkthrough tooltip tooltip-bottom"
              data-tip="Profile"
            >
              <div className="dropdown dropdown-end">
                <div
                  tabIndex="0"
                  role="button"
                  className="btn btn-circle avatar"
                  onClick={handleAvatarClick}
                >
                  {loggedInUser.email[0]}
                </div>
                <ul
                  tabIndex="0"
                  className={`menu menu-sm dropdown-content bg-black rounded-box z-[1] mt-3 w-52 p-2 shadow ${
                    dropdownOpen ? "block" : "hidden"
                  }`}
                >
                
                  <li>
                    <Link to="/mytrips">My Itineraries</Link>
                  </li>
                  <li>
                    <Link to="/myfinances">My Finances</Link>
                  </li>
                  <li>
                    <a onClick={handleLogout}>Logout</a>
                  </li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
      <dialog id="my_modal_4" className="modal">
        <div className="modal-box">
          <h3 className="font-bold text-lg">Travelify walkthrough</h3>
          <br />
          <div className="youtube-video-container">
            <iframe
              width="100%"
              height="315"
              src="https://www.youtube.com/embed/qF-uTDAzwPw?si=wGTHKm9Dja6ItYsY"
              title="YouTube video player"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          </div>
          <div className="modal-action">
            <form method="dialog">
              <button
                className="btn"
                onClick={() => document.getElementById("my_modal_4").close()}
              >
                Close
              </button>
            </form>
          </div>
        </div>
      </dialog>
      
    </>
  );
}

export default Navbar;
