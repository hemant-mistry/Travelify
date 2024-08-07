import { useState, useEffect } from "react";
import Datepicker from "react-tailwindcss-datepicker";
import geminiIcon from "../assets/GeminiIcon.png";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Lottie from "react-lottie";
import animationData from "../assets/lotties/globe.json";

function PlanInput({ loggedInUser }) {
  const defaultOptions = {
    loop: true,
    autoplay: true,
    animationData: animationData,
    rendererSettings: {
      preserveAspectRatio: "xMidYMid slice",
    },
  };

  const navigate = useNavigate();
  const [value, setValue] = useState({
    startDate: new Date(),
    endDate: new Date().setMonth(11),
  });
  const [stayDetails, setStayDetails] = useState("");
  const [numberOfDays, setNumberOfDays] = useState(0);
  const [budget, setBudget] = useState("");
  const [preferences, setPreferences] = useState({
    Landmarks: false,
    RooftopBars: false,
    Museums: false,
    Restaurants: false,
    PatioBars: false,
    CocktailBars: false,
    DanceClubs: false,
    DessertShops: false,
  });
  const [loading, setLoading] = useState(false);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);

  const loadingMessages = [
    "Building your itinerary...",
    "Gathering the best places to visit...",
    "Finding amazing restaurants and bars...",
    "Creating a memorable experience for you...",
    "Almost there...",
  ];

  useEffect(() => {
    let timer;
    if (loading && loadingMessageIndex < loadingMessages.length - 1) {
      timer = setInterval(() => {
        setLoadingMessageIndex((prevIndex) => prevIndex + 1);
      }, 1000); // Change message every 2 seconds
    }

    return () => {
      clearInterval(timer);
    };
  }, [loading, loadingMessageIndex]);

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
    setLoading(true);
    setLoadingMessageIndex(0); // Reset the loading message index

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
      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}generate-trip/`,
        data
      );
      console.log(response.data);
      // Redirect to /mytrips upon successful submission
      navigate("/mytrips");
    } catch (error) {
      console.error("There was an error saving the trip details!", error);
    } finally {
      // Set the final loading message index
      setLoadingMessageIndex(loadingMessages.length - 1);

      // Wait a bit before setting loading to false to show the final message
      setTimeout(() => setLoading(false), 2000);
    }
  };

  return (
    <>
      {loading ? (
        <div className="text-center items-center md:mt-[180px] sm:mt-[150px] text-primary text-xl">
          <Lottie options={defaultOptions} height={100} width={100} />
          {loadingMessages[loadingMessageIndex]}
        </div>
      ) : (
        <div className="mt">
          <div className="text-2xl md:text-3xl font-bold pl-4 md:pl-6">
            Tell us more about your <span className="text-primary">trip..</span>
          </div>
          <div className="pl-4 pr-6 pt-2 md:pl-6">
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Sunt amet
            quaerat aliquam tempora ducimus
          </div>
          <div className="p-6">
            <div>
              <label className="form-control w-full max-w-xs">
                <div className="label">
                  <span className="label-text text-sm md:text-sm text-white">
                    Where are you planning to go?
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
                    How many days are you planning to visit?
                  </span>
                </div>
                <Datepicker
                  value={value}
                  onChange={handleValueChange}
                  inputClassName={"input input-bordered w-full h-8"}
                />
              </label>
            </div>
            <br />
            <div>
              <label className="form-control w-full max-w-sm">
                <div className="label">
                  <span className="label-text text-sm md:text-sm text-white">
                    How much do you think you'll spend?
                  </span>
                </div>
                <p className="text-neutral-content text-xs pl-1">
                  Based on the budget preferences we will suggest your
                  restaurants
                </p>
                <input
                  type="range"
                  min={0}
                  max="100"
                  className="range range-sm mt-5"
                  step="50"
                />
                <div className="flex w-full justify-between px-2 text-xs md:text-sm mt-3">
                  <span>Frugal</span>
                  <span>Moderate</span>
                  <span>Expensive</span>
                </div>
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
                    <div className="ml-2">
                      {preference.split(/(?=[A-Z])/).join(" ")}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="divider"></div>
            <button
              onClick={handleSubmit}
              className="btn btn-sm mt-3"
              disabled={loading}
            >
              <img src={geminiIcon} alt="Login Icon" className="h-4 w-4" />
              Build Itinerary
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export default PlanInput;
