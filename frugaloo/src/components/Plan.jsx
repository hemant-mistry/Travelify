import googleMapIcon from "../assets/googleMapIcon.png";
import geminiIcon from "../assets/GeminiIcon.png";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import TickConfirmation from "../assets/TickConfirmation.png";
import DiscardConfirmation from "../assets/DiscardConfirmation.png";

function Plan({ loggedInUser }) {
  const { tripId } = useParams();
  const [planDetails, setPlanDetails] = useState([]); // State to hold fetched plan details
  const [loading, setLoading] = useState(false);
  const [selectedDay, setSelectedDay] = useState(null); // State to hold the selected day for confirmation
  const [completedDays, setCompletedDays] = useState([]); // State to hold completed days

  useEffect(() => {
    // Function to fetch plan details based on tripId
    const fetchPlanDetails = async () => {
      setLoading(true);
      try {
        const response = await axios.post(
          `${import.meta.env.VITE_BACKEND_URL}fetch-plan/`,
          { trip_id: tripId }
        );
        let generatedPlanString = response.data.generated_plan;
        console.log("Generated Plan String:", generatedPlanString); // Log the generated plan string

        // Ensure the plan string is wrapped in array brackets
        if (
          generatedPlanString[0] !== "[" &&
          generatedPlanString[generatedPlanString.length - 1] !== "]"
        ) {
          generatedPlanString = `[${generatedPlanString}]`;
        }

        // Replace occurrences of '},{' with '},{' to ensure valid JSON array format
        generatedPlanString = generatedPlanString.replace(/}, {/g, "},{");

        // Parse the plan details string into an array of objects
        const parsedPlanDetails = JSON.parse(generatedPlanString);
        console.log("Parsed", parsedPlanDetails);
        setPlanDetails(parsedPlanDetails);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching plan details:", error);
        setLoading(false);
      }
    };

    fetchPlanDetails(); // Fetch plan details when component mounts
  }, [tripId]); // Trigger fetch when tripId changes

  // Handle locate button click
  const handleLocateClick = (location) => {
    const url = `https://maps.google.com/?q=${location}`;
    window.open(url, "_blank");
  };

  // Handle confirm button click
  const handleConfirmClick = async (day) => {
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}update-progress/`,
        {
          user_id: loggedInUser.id,
          trip_id: tripId,
          progress: day.description
        }
      );
      console.log("Progress updated successfully:", response.data);
      // Update the completed days state
      setCompletedDays([...completedDays, day.day]);
      // Close the modal
      document.getElementById("my_modal_3").close();
    } catch (error) {
      console.error("Error updating progress:", error);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center mt-[300px] text-primary">
        <span className="loading loading-spinner loading-lg mr-5"></span>
        Loading itinerary..
      </div>
    );
  }

  return (
    <>
      <div className="text-center font-bold text-2xl lg:text-3xl">
        Your personalized{" "}
        <span className="text-primary">Itinerary.. {tripId}</span>
      </div>
      <div className="timeline-container p-10">
        <ul className="timeline timeline-snap-icon max-md:timeline-compact timeline-vertical">
          {planDetails &&
            planDetails.map((day, index) => (
              <li key={index}>
                <div className="timeline-middle">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill={completedDays.includes(day.day) ? "lightgreen" : "white"}
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
                    index % 2 === 0
                      ? "timeline-start md:text-end justify-start"
                      : "timeline-end md:text-start justify-end"
                  }`}
                >
                  <time className="font-bold italic text-primary">
                    Day {day.day}
                  </time>
                  <div className="text-lg font-black mt-2">
                    {day.place_name}
                  </div>
                  <p>{day.description}</p>
                  <div
                    className={`flex gap-2 mt-3 mb-5 justify-start ${
                      index % 2 === 0 ? "md:justify-end" : "md:justify-start"
                    }`}
                  >
                    {/* The button to open modal */}
                    <label
                      htmlFor={`my_modal_${index}`}
                      className="btn btn-xs md:btn-sm"
                    >
                      <img
                        src={geminiIcon}
                        alt="Gemini Icon"
                        className="h-6 w-6"
                      />
                      Ask Gemini
                    </label>
                    <input
                      type="checkbox"
                      id={`my_modal_${index}`}
                      className="modal-toggle"
                    />
                    <div className="modal" role="dialog">
                      <div className="modal-box flex items-center justify-center">
                        <div>
                          <div className="flex items-center justify-start mb-2">
                            <img
                              src={geminiIcon}
                              alt="Google Map Icon"
                              className="h-6 w-6 mr-2"
                            />
                            <h3 className="text-sm md:text-lg font-bold">
                              Unexpected turns? Want to change Itinerary?
                            </h3>
                          </div>
                          <div className="text-center">
                            <textarea
                              className="textarea textarea-bordered w-full max-w-md mx-auto mt-5"
                              rows={5}
                              placeholder="Describe the changes you want to make in the Itinerary..."
                            ></textarea>
                            <button className="btn btn-outline btn-primary btn-sm mt-5">
                              Get AI powered suggestions
                            </button>
                          </div>
                        </div>
                      </div>
                      <label
                        className="modal-backdrop"
                        htmlFor={`my_modal_${index}`}
                      >
                        Close
                      </label>
                    </div>
                    <button
                      className="btn btn-xs md:btn-sm"
                      onClick={() =>
                        handleLocateClick(day.latitude_and_longitude)
                      }
                    >
                      <img
                        src={googleMapIcon}
                        alt="Google Map Icon"
                        className="h-6 w-6"
                      />
                      Locate
                    </button>
                    {/* You can open the modal using document.getElementById('ID').showModal() method */}
                    <button
                      className="btn btn-success btn-xs md:btn-sm"
                      onClick={() => {
                        setSelectedDay(day);
                        document.getElementById("my_modal_3").showModal();
                      }}
                    >
                      Mark as completed?
                    </button>
                    <dialog id="my_modal_3" className="modal">
                      <div className="modal-box max-w-sm">
                        <form method="dialog">
                          {/* if there is a button in form, it will close the modal */}
                          <button className="btn btn-sm btn-circle btn-ghost absolute right-2 top-4">
                            ✕
                          </button>
                        </form>
                        <h3 className="font-bold text-sm md:text-lg text-left">
                          Confirmation
                        </h3>
                        <p className="py-4 text-sm md:text-lg text-left">
                          Are you sure you want to mark this day as completed?
                        </p>
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
                        <button className="btn btn-sm btn-error ml-5">
                          <img
                            src={DiscardConfirmation}
                            alt="Login Icon"
                            className="h-4 w-4"
                          />
                          Discard
                        </button>
                      </div>
                    </dialog>
                  </div>
                </div>
                <hr className={completedDays.includes(day.day) ? "bg-green-500" : ""} />
              </li>
            ))}
        </ul>
      </div>
    </>
  );
}

export default Plan;
