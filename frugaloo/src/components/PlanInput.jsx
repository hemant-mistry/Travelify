import { useState } from "react";
import Datepicker from "react-tailwindcss-datepicker";
import geminiIcon from "../assets/GeminiIcon.png";
import axios from "axios";

function PlanInput({ loggedInUser }) {
  const [value, setValue] = useState({
    startDate: new Date(),
    endDate: new Date().setMonth(11),
  });
  const [stayDetails, setStayDetails] = useState("");
  const [numberOfDays, setNumberOfDays] = useState(0);
  const [budget, setBudget] = useState("");
  const [preferences, setPreferences] = useState({
    landmarks: false,
    rooftopBars: false,
    museums: false,
    restaurants: false,
    patioBars: false,
    cocktailBars: false,
    danceClubs: false,
    dessertShops: false,
  });

  const handleValueChange = (newValue) => {
    setValue(newValue);

    // Calculate the number of days
    const start = new Date(newValue.startDate);
    const end = new Date(newValue.endDate);
    const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
    setNumberOfDays(days);
  };

  const handlePreferencesChange = (event) => {
    const { name, checked } = event.target;
    setPreferences((prev) => ({
      ...prev,
      [name]: checked,
    }));
  };

  const handleSubmit = async () => {
    const additionalPreferences = Object.keys(preferences)
      .filter((key) => preferences[key])
      .join(", ");

    const data = {
      user_id: loggedInUser.id,
      stay_details: stayDetails,
      number_of_days: numberOfDays,
      budget: budget,
      additional_preferences: additionalPreferences,
    };

    try {
      const response = await axios.post("http://127.0.0.1:8000/save-trip-details/", data);
      console.log(response.data);
    } catch (error) {
      console.error("There was an error saving the trip details!", error);
    }
  };

  return (
    <>
      <div className="mt">
        <div className="text-2xl md:text-3xl font-bold pl-4 md:pl-6">
          Tell us more about your <span className="text-primary">trip..</span>
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
              <span className="label-text text-sm md:text-sm text-white">
                Enter your stay details :
              </span>
            </div>
            <input
              type="text"
              value={stayDetails}
              onChange={(e) => setStayDetails(e.target.value)}
              placeholder="Type here"
              className="input input-bordered w-full max-w-xs input-sm md:input-sm"
            />
          </label>
        </div>
        <br />
        <div>
          <label className="form-control w-full max-w-sm md:max-w-lg">
            <div className="label">
              <span className="label-text text-sm md:text-sm text-white">
                How many days are you planning to stay:
              </span>
            </div>
            <Datepicker value={value} onChange={handleValueChange} inputClassName={"input input-bordered w-full h-8"} />
          </label>
        </div>
        <br />
        <div>
          <label className="form-control w-full max-w-xs">
            <div className="label">
              <span className="label-text text-sm md:text-sm text-white">
                Enter your estimated budget :
              </span>
            </div>
            <input
              type="text"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              placeholder="Type here"
              className="input input-bordered w-full max-w-xs input-sm md:input-sm"
            />
          </label>
        </div>
        <br />
        <div>
          <div className="label">
            <span className="label-text text-sm md:text-sm text-white">
              Let us know if you got any additional preferences :
            </span>
          </div>
          <div className="flex flex-wrap md:flex-nowrap gap-10 mt-5">
            {Object.keys(preferences).map((preference) => (
              <div key={preference} className="flex whitespace-nowrap">
                <div>
                  <input
                    type="checkbox"
                    name={preference}
                    checked={preferences[preference]}
                    onChange={handlePreferencesChange}
                    className="checkbox"
                  />
                </div>
                <div className="ml-2">{preference.split(/(?=[A-Z])/).join(" ")}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="divider"></div>
        <button onClick={handleSubmit} className="btn btn-sm mt-3">
          <img src={geminiIcon} alt="Login Icon" className="h-4 w-4" />
          Build Itinerary
        </button>
      </div>
    </>
  );
}

export default PlanInput;
