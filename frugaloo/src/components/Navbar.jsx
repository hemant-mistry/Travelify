import { Link } from "react-router-dom";
import { useState } from "react";
import helpicon from "../assets/helpicon.png";
import loginIcon from "../assets/loginIcon.png";

function Navbar() {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false); // State to track login status

  const handleAvatarClick = () => {
    setDropdownOpen(!dropdownOpen);
  };

  const handleLogin = () => {
    // Logic to handle login (e.g., set isLoggedIn to true)
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    // Logic to handle logout (e.g., set isLoggedIn to false)
    setIsLoggedIn(false);
    setDropdownOpen(false); // Close dropdown on logout
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
          {!isLoggedIn && ( // Show login button if not logged in
            <Link to="/login" className="btn btn-ghost btn-md">
              <img src={loginIcon} alt="Login Icon" className="h-6 w-6" />
              Login/SignUp
            </Link>
          )}
          {isLoggedIn && ( // Show avatar if logged in
            <div className="dropdown dropdown-end">
              <div
                tabIndex="0"
                role="button"
                className="btn btn-ghost btn-circle avatar"
                onClick={handleAvatarClick}
              >
                <div className="w-10 rounded-full">
                  <img
                    alt="Avatar"
                    src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.jpg"
                  />
                </div>
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
