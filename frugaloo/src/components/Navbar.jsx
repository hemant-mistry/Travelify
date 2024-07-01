import { useState } from "react";
import helpicon from "../assets/helpicon.png";

function Navbar() {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const handleAvatarClick = () => {
    setDropdownOpen(!dropdownOpen);
  };
  return (
    <>
      <div className="navbar bg-base-100 rounded-md">
        <div className="flex-1">
          <a className="btn btn-ghost text-xl">Frugaloo</a>
        </div>
        <div className="flex-none">
          <div className="help">
            <button className="btn btn-ghost mr-2" onClick={() => document.getElementById('my_modal_4').showModal()}>
              <img src={helpicon} alt="Help Icon" className="h-6 w-6" />
            </button>
          </div>
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
              className={`menu menu-sm dropdown-content bg-base-100 rounded-box z-[1] mt-3 w-52 p-2 shadow ${
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
                <a>Logout</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
      <dialog id="my_modal_4" className="modal">
        <div className="modal-box">
          <h3 className="font-bold text-lg">Frugaloo walkthrough</h3>
          <br/>
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
              {/* if there is a button, it will close the modal */}
              <button className="btn" onClick={() => document.getElementById('my_modal_4').close()}>Close</button>
            </form>
          </div>
        </div>
      </dialog>
    </>
  );
}

export default Navbar;
