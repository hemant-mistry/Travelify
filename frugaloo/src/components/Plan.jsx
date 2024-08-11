import googleMapIcon from "../assets/googleMapIcon.png";
import geminiIcon from "../assets/GeminiIcon.png";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import TickConfirmation from "../assets/TickConfirmation.png";
import DiscardConfirmation from "../assets/DiscardConfirmation.png";
import animationData from "../assets/lotties/gemini.json";
import geminiData from "../assets/lotties/gemini-logo.json";
import promptGuide from "../assets/promptGuide.png";
import Lottie from "react-lottie";
import QuoteComponent from "./Quotes";
function Plan({ loggedInUser, onLocateClick, budget }) {
  const defaultOptions = {
    loop: true,
    autoplay: true,
    animationData: animationData,
    rendererSettings: {
      preserveAspectRatio: "xMidYMid slice",
    },
  };

  const geminiAnimationOptions = {
    loop: true,
    autoplay: true,
    animationData: geminiData,
    rendererSettings: {
      preserveAspectRatio: "xMidYMid Slice",
    },
  };
  const navigate = useNavigate();
  const { tripId } = useParams();
  const [planDetails, setPlanDetails] = useState([]); // State to hold fetched plan details
  const [loading, setLoading] = useState(false);
  const [selectedDay, setSelectedDay] = useState(null); // State to hold the selected day for confirmation
  const [completedDays, setCompletedDays] = useState([]); // State to hold completed days
  const [currentDay, setCurrentDay] = useState(1); // State to hold the current day
  const [userChanges, setUserChanges] = useState(""); // State to hold the user input
  const [planChanges, setPlanChanges] = useState(""); // State to hold the changes from the plan
  const [suggestionsModal, setSuggestionsModal] = useState(false);
  const [newPlan, setNewPlan] = useState([]);
  const [modalLoading, setModalLoading] = useState(false);
  const [suggestionloading, setSuggestionLoading] = useState(false);
  const [error, setError] = useState(""); // State to hold error message
  const [errorTimeout, setErrorTimeout] = useState(null);
  const [retryCountdown, setRetryCountdown] = useState(0); // State for countdown

  useEffect(() => {
    // Function to fetch plan details based on tripId
    const fetchPlanDetails = async () => {
      setLoading(true);
      try {
        const response = await axios.post(
          `${import.meta.env.VITE_BACKEND_URL}fetch-plan/`,
          { trip_id: tripId }
        );

        const outerData = response.data;
        const innerDataString = outerData.generated_plan;
        const generated_plan = JSON.parse(innerDataString);
        const parsedPlanDetails = Object.values(generated_plan);
        setPlanDetails(parsedPlanDetails);
      } catch (error) {
        console.error("Error fetching plan details:", error);
      } finally {
        setLoading(false);
      }
    };

    const fetchPlanProgress = async () => {
      try {
        const response = await axios.post(
          `${import.meta.env.VITE_BACKEND_URL}fetch-trip-progress/`,
          { trip_id: tripId }
        );
        const completedDaysArray = response.data.map((day) => day.day);
        setCompletedDays(completedDaysArray);
        // Set the current day based on completed days
        setCurrentDay(completedDaysArray.length + 1);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching plan details:", error);
        setLoading(false);
      }
    };
    fetchPlanDetails();
    fetchPlanProgress();
  }, [tripId]);

  // Countdown effect
  useEffect(() => {
    if (retryCountdown > 0) {
      const timer = setInterval(() => {
        setRetryCountdown((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [retryCountdown]);

  const handleLocateClick = (dayData, dayIndex, trip_id) => {
    onLocateClick(dayData); // Pass day data to parent

    navigate(`/locate/${trip_id}/${dayIndex + 1}`);
  };

  const handleConfirmClick = async (day) => {
    try {
      console.log("day", day);
      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}update-progress/`,
        {
          user_id: loggedInUser.id,
          trip_id: tripId,
          day: day,
        }
      );
      // Update the completed days state
      setCompletedDays([...completedDays, parseInt(day)]);
      console.log(completedDays);
      // Move to the next day
      setCurrentDay(currentDay + 1);
      // Close the modal
      document.getElementById("my_modal_3").close();
    } catch (error) {
      console.error("Error updating progress:", error);
    }
  };

  const handleAskGeminiClick = async (day) => {
    setModalLoading(true);
    setError(""); // Clear previous error message
    setRetryCountdown(5); // Set countdown for 5 seconds

    if (errorTimeout) {
      clearTimeout(errorTimeout);
      setErrorTimeout(null);
    }

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}gemini-suggestions/`,
        {
          trip_id: tripId,
          current_day: day,
          original_plan: planDetails,
          user_changes: userChanges,
          budget: budget,
        }
      );

      const outerData =
        typeof response.data === "string"
          ? JSON.parse(response.data)
          : response.data;

      const innerDataString = outerData.response_data;
      const parsedPlanDetailsRaw =
        typeof innerDataString === "string"
          ? JSON.parse(innerDataString)
          : innerDataString;

      const changes = parsedPlanDetailsRaw.changes || "";
      setPlanChanges(changes);

      const new_plan = parsedPlanDetailsRaw.generated_plan || "";
      const parsedPlanDetails = Object.values(new_plan);

      setNewPlan(parsedPlanDetails);
      setSuggestionsModal(true);
    } catch (error) {
      console.error("Error fetching the original plan", error);
      setError(
        "There was an error fetching the suggestions. Please try again."
      );

      const timeoutId = setTimeout(() => {
        setError("");
        setRetryCountdown(5); // Reset countdown when the error message disappears
      }, 5000);

      setErrorTimeout(timeoutId);
    } finally {
      setModalLoading(false);
    }
  };

  const handleDiscardClick = () => {
    setNewPlan("");
    setSuggestionsModal(false);
    document.getElementById("my_modal_5").close();
  };

  const handleSuggestionClick = async () => {
    setUserChanges("");
    setSuggestionLoading(true);
    setPlanDetails(newPlan);
    console.log("newplan", JSON.stringify(newPlan));
    //Updating the trip info in the database
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}update-plan/`,
        {
          trip_id: tripId,
          new_plan: newPlan,
        }
      );
    } catch (error) {
      console.error("Error fetching the original plan", error);
    }

    document.getElementById("my_modal_5").close();
    setSuggestionLoading(false);
    setSuggestionsModal(false);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center pt-[300px] font-lato">
        <span className="loading loading-spinner loading-lg mr-5 text-custom-blue"></span>
        Loading Itinerary..
      </div>
    );
  }

  return (
    <>
      <div className="text-center font-bold text-2xl lg:text-3xl pt-[80px]">
        Your personalized Itinerary
      </div>
      <div className="timeline-container p-10">
        <ul className="timeline timeline-snap-icon max-md:timeline-compact timeline-vertical">
          {planDetails &&
            planDetails.map((dayActivities, dayIndex) => (
              <li key={dayIndex}>
                <div className="timeline-middle">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill={
                      completedDays.includes(dayIndex + 1)
                        ? "lightgreen"
                        : "white"
                    }
                    className="h-5 w-5"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div
                  className={`mb-10 ${
                    (dayIndex + 1) % 2 === 0
                      ? "timeline-start md:text-end justify-start"
                      : "timeline-end md:text-start justify-end"
                  }`}
                >
                  <time className="font-bold italic text-custom-light-blue">
                    Day {dayIndex + 1}
                  </time>
                  {dayActivities.map((activity, activityIndex) => (
                    <div key={activityIndex} className="mb-5">
                      <div className="text-lg font-black mt-2">
                        <a
                          className="link link-hover"
                          href={`https://maps.google.com/?q=${
                            activity.place_name || activity.lat_long
                          }`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {activity.place_name ||
                            activity.restaurant_name ||
                            activity.night_club_name}
                        </a>
                      </div>
                      <p>{activity.description}</p>
                      <p className="text-neutral-content text-xs">
                        Estimated time for exploring: {activity.TOE}
                      </p>
                    </div>
                  ))}

                  {currentDay === dayIndex + 1 && (
                    <div
                      className={`flex gap-2 mt-3 mb-5 justify-start ${
                        (dayIndex + 1) % 2 === 0
                          ? "md:justify-end"
                          : "md:justify-start"
                      }`}
                    >
                      <>
                        <button
                          className="btn btn-xs md:btn-sm bg-base-200"
                          onClick={() =>
                            document.getElementById(`my_modal_5`).showModal()
                          }
                        >
                          <Lottie
                            options={defaultOptions}
                            height={20}
                            width={20}
                          />
                          Ask Gemini
                        </button>
                        <dialog id="my_modal_5" className="modal">
                          <div className="modal-box flex items-start justify-center min-h-sm">
                            <form method="dialog">
                              <button className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">
                                ✕
                              </button>
                            </form>
                            {modalLoading ? (
                              <div className="flex justify-center items-center text-primary gap-2 h-[150px]">
                               
                                      <QuoteComponent /> 
                              </div>
                            ) : (
                              <div>
                                {suggestionsModal ? (
                                  <>
                                    {suggestionloading ? (
                                      <div className="flex flex-row items-center justify-center p-5">
                                        <span className="loading loading-spinner text-primary loading-md mr-5"></span>
                                        Applying changes...
                                      </div>
                                    ) : (
                                      <>
                                        <div className="flex items-center justify-start mb-2">
                                          <img
                                            src={geminiIcon}
                                            alt="Gemini Icon"
                                            className="h-6 w-6 mr-2"
                                          />
                                          <h3 className="text-sm md:text-lg font-bold">
                                            Gemini generated suggestions..
                                          </h3>
                                        </div>
                                        <div className="text-left mt-5">
                                          {planChanges}
                                        </div>
                                        <div className="flex justify-end items-end mt-10">
                                          <button
                                            className="btn btn-sm btn-success"
                                            onClick={() =>
                                              handleSuggestionClick()
                                            }
                                          >
                                            <img
                                              src={TickConfirmation}
                                              alt="Confirm Icon"
                                              className="h-4 w-4"
                                            />
                                            Confirm
                                          </button>
                                          <button
                                            className="btn btn-sm btn-error ml-5"
                                            onClick={() =>
                                              setSuggestionsModal(false)
                                            }
                                          >
                                            <img
                                              src={DiscardConfirmation}
                                              alt="Discard Icon"
                                              className="h-4 w-4"
                                            />
                                            Discard
                                          </button>
                                        </div>
                                      </>
                                    )}
                                  </>
                                ) : (
                                  <>
                                    <div className="flex items-center justify-start mb-2">
                                      <Lottie
                                        options={defaultOptions}
                                        height={20}
                                        width={20}
                                      />
                                      <h3 className="text-sm md:text-lg font-bold ml-2">
                                        Unexpected turns? Want to change
                                        Itinerary?
                                      </h3>
                                    </div>
                                    {error ? (
                                      <div className="text-red-500 text-center mt-4">
                                        {error}{" "}
                                        {retryCountdown > 0 &&
                                          `Retry in ${retryCountdown} seconds`}
                                      </div>
                                    ) : (
                                      <div className="text-center relative w-full max-w-md mx-auto mt-5">
                                        <div className="relative">
                                          <textarea
                                            className="textarea textarea-bordered w-full"
                                            rows={5}
                                            placeholder="Describe the changes you want to make in the Itinerary..."
                                            onChange={(e) =>
                                              setUserChanges(e.target.value)
                                            }
                                            style={{ paddingBottom: "3rem" }} // Adding padding to the bottom for space
                                          ></textarea>
                                          <div className="absolute bottom-2 right-2">
                                            <button
                                              className="btn btn-sm btn-ghost flex items-center"
                                              onClick={() => {
                                                document
                                                  .getElementById("my_prompt_guide_modal")
                                                  .showModal();
                                              }}
                                            >
                                              <img
                                                src={promptGuide}
                                                alt="Prompt Guide Icon"
                                                className="h-4 w-4"
                                              />
                                            </button>
                                          </div>
                                        </div>
                                        <button
                                          className="btn btn-outline btn-primary btn-sm mt-5"
                                          onClick={() =>
                                            handleAskGeminiClick(currentDay)
                                          }
                                        >
                                          Get AI powered suggestions
                                        </button>
                                      </div>
                                    )}
                                  </>
                                )}
                              </div>
                            )}
                          </div>
                        </dialog>
                      </>

                      <dialog id="my_prompt_guide_modal" className="modal">
                        <div className="modal-box">
                          <form method="dialog">
                            {/* if there is a button in form, it will close the modal */}
                            <button className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">
                              ✕
                            </button>
                          </form>
                          <h3 className="font-bold text-lg">Prompt Guide</h3>
                          <p className="py-4 text-sm">
                            Below are some of the prompts highlighting various
                            capabilities...
                          </p>
                          <ul>
                            <p className="py-2 text-md">
                              <u>Change itinerary based on theme</u>
                            </p>

                            <li className="text-sm">
                              - Dedicate the day to activites related to art
                            </li>
                            <li className="text-sm">
                              - Dedicate the day to activites related to culture
                            </li>
                            <li className="text-sm">
                              - Dedicate the day to activites related to
                              culinary experiences
                            </li>
                            <li className="text-sm">
                              - Dedicate the day to activites related to family
                            </li>

                            <p className="py-2 text-md">
                              <u>Change itinerary based on food choice</u>
                            </p>
                            <li className="text-sm">
                              - Recommend street food for evening
                            </li>
                            <li className="text-sm">
                              - Recommend an Ice cream shop to end the day.
                            </li>
                            <li className="text-sm">
                              - Recommend a dessert shop.
                            </li>
                            <li className="text-sm">
                              - Change cuisine of the restaurants to indian,
                              italian and lebanese
                            </li>
                            <p className="py-2 text-md">
                              <u>Add activities based on your mood</u>
                            </p>
                            <li className="text-sm">
                              - Recommend some nightclub.
                            </li>
                            <li className="text-sm">
                              - Recommend some beach activites
                            </li>

                            <p className="py-3 text-sm">
                              If that's not sufficient, you can also adjust an
                              entire day of the itinerary or even the entire
                              itinerary.
                            </p>
                          </ul>
                        </div>
                      </dialog>
                      <button
                        className="btn btn-xs md:btn-sm bg-base-200"
                        onClick={() =>
                          handleLocateClick(dayActivities, dayIndex, tripId)
                        } // Pass day data
                      >
                        <img
                          src={googleMapIcon}
                          alt="Google Map Icon"
                          className="h-6 w-6"
                        />
                        Locate
                      </button>

                      <button
                        className="relative inline-flex items-center justify-center px-10 py-4 overflow-hidden bg-base-200 text-gray rounded-lg group btn-xs md:btn-sm"
                        onClick={() => {
                          setSelectedDay(dayIndex + 1);
                          document.getElementById("my_modal_3").showModal();
                        }}
                      >
                        <span className="absolute w-0 h-0 transition-all duration-500 ease-out bg-success rounded-full group-hover:w-56 group-hover:h-56 text-black"></span>
                        <span className="absolute inset-0 w-full h-full -mt-1 rounded-lg "></span>
                        <span className="relative font-bold">
                          Mark it as completed?
                        </span>
                      </button>

                      <dialog id="my_modal_3" className="modal">
                        <div className="modal-box max-w-sm">
                          <form method="dialog">
                            <button className="btn btn-sm btn-circle btn-ghost absolute right-2 top-4">
                              ✕
                            </button>
                          </form>
                          <h3 className="font-bold text-sm md:text-lg text-left">
                            Confirmation
                          </h3>
                          <p className="py-4 text-sm md:text-lg text-center">
                            Are you sure you want to mark this day as completed?
                          </p>
                          <div className="flex justify-center">
                            <button
                              className="btn btn-sm btn-success"
                              onClick={() => handleConfirmClick(selectedDay)}
                            >
                              <img
                                src={TickConfirmation}
                                alt="Login Icon"
                                className="h-4 w-4"
                              />
                              Confirm
                            </button>
                            <button
                              className="btn btn-sm btn-error ml-5"
                              onClick={handleDiscardClick}
                            >
                              <img
                                src={DiscardConfirmation}
                                alt="Login Icon"
                                className="h-4 w-4"
                              />
                              Discard
                            </button>
                          </div>
                        </div>
                      </dialog>
                    </div>
                  )}
                </div>
                <hr
                  className={`transition-all duration-1000 ease-in-out ${
                    completedDays.includes(dayIndex + 1)
                      ? "bg-green-500 animate-fill"
                      : ""
                  }`}
                />
              </li>
            ))}
        </ul>
      </div>
    </>
  );
}

export default Plan;
