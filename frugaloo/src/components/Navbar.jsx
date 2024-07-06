import { Link } from "react-router-dom";
import { useState } from "react";
import helpicon from "../assets/helpicon.png";
import loginIcon from "../assets/loginIcon.png";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient('https://wqbvxqxuiwhmretkcjaw.supabase.co', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndxYnZ4cXh1aXdobXJldGtjamF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTk3MTYyMTQsImV4cCI6MjAzNTI5MjIxNH0.CXyPAdKKgwjmPee0OmvV4BxnQUj_4y3ARbaEuSToz6s')


// eslint-disable-next-line react/prop-types
function Navbar({ loggedInUser }) { // Destructure loggedInUser
  const [dropdownOpen, setDropdownOpen] = useState(false);
 
  const handleAvatarClick = () => {
    setDropdownOpen(!dropdownOpen);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    window.location.reload();
  };

  return (
    <>
      <div className="navbar rounded-md">
        <div className="flex-1">
          <Link to="/" className="btn btn-ghost text-xl">Travelify</Link>
        </div>
        <div className="flex-none">
          <div className="help">
            <button
              className="btn btn-ghost mr-2"
              onClick={() => document.getElementById("my_modal_4").showModal()}
            >
              <img src={helpicon} alt="Help Icon" className="h-6 w-6" />
            </button>
          </div>
          {!loggedInUser && ( // Show login button if not logged in
            <Link to="/login" className="btn btn-ghost btn-md">
              <img src={loginIcon} alt="Login Icon" className="h-6 w-6" />
              Login/SignUp
            </Link>
          )}
          {loggedInUser && ( // Show avatar if logged in
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
                  <a className="justify-between">
                    Profile
                    <span className="badge">New</span>
                  </a>
                </li>
                <li>
                  <a>Settings</a>
                </li>
                <li>
                  <a onClick={handleLogout}>Logout</a>
                </li>
              </ul>
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
              src="https://www.youtube.com/embed/_TVnM9dmUSk"
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
