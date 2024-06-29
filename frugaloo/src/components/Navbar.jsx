import { useState } from "react";

function Navbar() {
const [dropdownOpen, setDropdownOpen] = useState(false);
const handleAvatarClick = () => {
    setDropdownOpen(!dropdownOpen);
  };
  return (
    <>
    <div class="navbar bg-base-100 rounded-md">
  <div class="flex-1">
    <a class="btn btn-ghost text-xl">Frugaloo</a>
  </div>
  <div class="flex-none">
    <div class="dropdown dropdown-end">
      <div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar" onClick={handleAvatarClick}>
        <div class="w-10 rounded-full">
          <img
            alt="Tailwind CSS Navbar component"
            src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.jpg" />
        </div>
      </div>
      <ul
              tabIndex="0"
              className={`menu menu-sm dropdown-content bg-base-100 rounded-box z-[1] mt-3 w-52 p-2 shadow ${
                dropdownOpen ? 'block' : 'hidden'
              }`}
            >
        <li>
          <a class="justify-between">
            Profile
            <span class="badge">New</span>
          </a>
        </li>
        <li><a>Settings</a></li>
        <li><a>Logout</a></li>
      </ul>
    </div>
  </div>
</div>
    </>
  );
}

export default Navbar;
