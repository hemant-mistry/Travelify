import { useState, useEffect } from "react";
import Datepicker from "react-tailwindcss-datepicker";
import geminiIcon from "../assets/GeminiIcon.png";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Lottie from "react-lottie";
import animationData from "../assets/lotties/globe.json";

function PlanInput({ loggedInUser, budget, setBudget }) {
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
  const [error, setError] = useState(null);

  const loadingMessages = [
    "Building your itinerary...",
    "Gathering the best places to visit...",
    "Finding amazing restaurants and bars...",
    "Creating a memorable experience for you...",
    "Almost there...",
  ];

  const errorMessages = [
    "Our AI took a wrong turn in the data highway. Don’t worry, it’s rerouting. Please try again.",
    "Our AI is having a brain fart. Let’s try that again, shall we? We promise to make it worth your while.",
    "Abracadabra! Our magic wand isn’t working quite right. Let’s try another spell.",
    "We’re experiencing a brief moment of ‘thinking too hard’. Let’s try that again, shall we?",
  ];

  useEffect(() => {
    let timer;
    if (loading && loadingMessageIndex < loadingMessages.length - 1) {
      timer = setInterval(() => {
        setLoadingMessageIndex((prevIndex) => prevIndex + 1);
      }, 1000); // Change message every 1 second
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

  const handleBudgetChange = (event) => {
    const value = event.target.value;
    let budgetLabel = 1;
    if (value > 0 && value <= 50) {
      budgetLabel = 2;
    } else if (value > 50) {
      budgetLabel = 3;
    }
    setBudget(budgetLabel);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setLoadingMessageIndex(0); // Reset the loading message index
    setError(null); // Reset the error state

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
        `${import.meta.env.VITE_BACKEND_URL}pre-plan-trip/`,
        data
      );

      const dataReceivedfromPhase1 = response.data.response_data;
      const data2 = {
        user_id: loggedInUser.id,
        stay_details: stayDetails,
        number_of_days: numberOfDays,
        budget: budget,
        additional_preferences: additionalPreferences,
        response_data: dataReceivedfromPhase1,
      };

      console.log(response.data.response_data);
      const response2 = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}generate-trip/`,
        data2
      );
      console.log(response2.data);
      // Redirect to /mytrips upon successful submission
      navigate("/mytrips");
    } catch (error) {
      console.error("There was an error saving the trip details!", error);
      // Randomize error message
      const randomErrorMessage =
        errorMessages[Math.floor(Math.random() * errorMessages.length)];
      setError(randomErrorMessage);
    } finally {
      // Set the final loading message index
      setLoadingMessageIndex(loadingMessages.length - 1);

      // Wait a bit before setting loading to false to show the final message
      setTimeout(() => setLoading(false), 2000);
    }
  };

  const handleRetry = () => {
    handleSubmit();
  };

  return (
    <>
      {loading ? (
        <div className="text-center items-center md:pt-[200px] pt-[250px] text-primary text-xl">
          <Lottie options={defaultOptions} height={100} width={100} />
          {loadingMessages[loadingMessageIndex]}
        </div>
      ) : (
        <>
          {error && (
            <div
              id="error-modal"
              className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-75 z-50"
              aria-labelledby="modal-title"
              role="dialog"
              aria-modal="true"
            >
              <div className="relative bg-[#0e1111] p-6 rounded-lg max-w-sm mx-auto">
                <button
                  type="button"
                  className="absolute top-3 right-3 text-gray-400 hover:text-gray-600"
                  data-modal-toggle="error-modal"
                  onClick={() => setError(null)}
                >
                  <span className="sr-only">Close</span>
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M6 18L18 6M6 6l12 12"
                    ></path>
                  </svg>
                </button>
                <h3
                  className="text-lg font-semibold text-white mt-[-15px]"
                  id="modal-title"
                >
                  Ran into a problem
                </h3>
                <p className="mt-2 text-sm text-custom-gray">{error}</p>
                <button
                  type="button"
                  className="btn btn-xs justify-center mt-4 inline-flex items-center   text-sm font-medium text-white bg-red-500 rounded-lg shadow-sm hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500"
                  onClick={handleRetry}
                >
                  Retry
                </button>
              </div>
            </div>
          )}
          <div className="pt-[80px]">
            <div className="text-2xl md:text-3xl font-bold pl-4 md:pl-6">
              Ready to map out your {" "}
              <span className="text-custom-light-blue">next journey </span>
            </div>
            <div className="pl-4 pr-6 pt-2 md:pl-6">
            Get started by entering your destination, travel dates, and budget to craft your ideal itinerary!

            </div>
            <div className="p-6">
              <div>
                <label className="form-control w-full max-w-xs">
                  <div className="label">
                    <span className="label-text text-sm md:text-sm text-white">
                    Where will your next adventure take you?
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
                    How long will you be exploring?
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
                    What’s your travel budget like?
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
                    value={(budget - 1) * 50}
                    className="range range-sm mt-5"
                    step="50"
                    onChange={handleBudgetChange}
                  />
                  <div className="flex w-full justify-between px-2 text-xs md:text-sm mt-3 ">
                  <div className="tooltip tooltip-right " data-tip="Great value for your money">

                    <span>Budget-Savvy</span>
                    </div>
                    <div className="tooltip tooltip-bottom " data-tip="Perfect balance of cost and quality.">
                    <span>Sweet Spot</span>
                    </div>
                    <div className="tooltip tooltip-bottom " data-tip="Premium experiences without compromise.">
                    <span>Treat Yourself</span>
                    </div>
                  </div>
                </label>
              </div>
              <br />

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
        </>
      )}
    </>
  );
}

export default PlanInput;
