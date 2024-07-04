import { useState } from "react";
import Datepicker from "react-tailwindcss-datepicker";
import geminiIcon from "../assets/GeminiIcon.png";
function PlanInput() {
  const [value, setValue] = useState({
    startDate: new Date(),
    endDate: new Date().setMonth(11),
  });

  const handleValueChange = (newValue) => {
    console.log("newValue:", newValue);
    setValue(newValue);
  };
  return (
    <>
      <div className="mt-5">
        <div className="text-2xl md:text-3xl font-bold pl-4 md:pl-6">
          Tell us more about your trip..
        </div>
        <div className="pl-4 pr-6 pt-2 md:pl-6">
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Sunt amet
          quaerat aliquam tempora ducimus
        </div>
      </div>
      <div className="p-6">
        <div>
          <label className="form-control w-full max-w-xs">
            <div className="label">
              <span className="label-text text-sm md:text-lg text-white">
                Enter your stay details :
              </span>
            </div>
            <input
              type="text"
              placeholder="Type here"
              className="input input-bordered w-full max-w-xs input-sm md:input-sm"
            />
          </label>
        </div>
        <br />
        <div>
          <label className="form-control w-full max-w-sm md:max-w-lg">
            <div className="label">
              <span className="label-text text-sm md:text-lg text-white">
                How many days are you planning to stay:
              </span>
            </div>
            <Datepicker value={value} onChange={handleValueChange} />
          </label>
        </div>
        <br />
        <div>
          <div className="label">
            <span className="label-text text-sm md:text-lg text-white">
              Enter your budget (in USD):
            </span>
          </div>
          <label className="input input-bordered flex items-center gap-2 max-w-sm md:max-w-lg">
            <input type="text" className="grow" placeholder="Email" />
          </label>
        </div>
        <br />
        <div>
          <label className="form-control w-full max-w-md">
            <div className="label">
              <span className="label-text text-sm md:text-lg text-white">
                Let us know if you got any additional preferences :
              </span>
            </div>
            <textarea
              className="textarea textarea-bordered"
              placeholder="Dump it out"
            ></textarea>
          </label>
        </div>
        <div className="divider"></div>

        <button className="btn btn-sm mt-3">
          <img src={geminiIcon} alt="Login Icon" className="h-4 w-4" />
          Build Itinerary
        </button>
      </div>
    </>
  );
}

export default PlanInput;
