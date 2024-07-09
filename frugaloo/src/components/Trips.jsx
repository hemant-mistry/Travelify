import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
function Trip({ loggedInUser }) {
  const [tripDetails, setTripDetails] = useState([]);
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();
  useEffect(() => {
    async function fetchTripDetails() {
      try {
        const response = await axios.post(
         `${import.meta.env.VITE_BACKEND_URL}fetch-trip-details/`,
          {
            user_id: loggedInUser.id,
          }
        );
        setTripDetails(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching trip details:", error);
        setLoading(false);
      }
    }

    fetchTripDetails();
  }, [loggedInUser]);

  const handleViewClick = (tripId) => {
    navigate(`/plan/${tripId}`);
  };

  if (loading) {
    return <div>Loading trip details...</div>;
  }

  return (
    <>
      <div className="text-2xl md:text-3xl font-bold pl-4 md:pl-6">
        My Itineraries
      </div>
      <div className="flex flex-wrap justify-start">
        {tripDetails.map((trip, index) => (
          <div key={index} className="max-w-xs mx-auto md:mx-5 mt-10">
            <div className="card bg-base-100 shadow-xl">
              <div className="card-body text-sm">
                <h2 className="card-title text-md">{trip.stay_details}</h2>
                <p><b>Preferences: </b>{trip.additional_preferences}</p>
                <p><b>Number of days: </b>{trip.number_of_days}</p>
                <div className="card-actions justify-end">
                  <button
                    className="btn btn-primary btn-sm mt-5"
                    onClick={() => handleViewClick(trip.trip_id)}
                  >
                    View
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

export default Trip;
