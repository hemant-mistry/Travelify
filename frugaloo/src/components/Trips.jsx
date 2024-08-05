import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function Trip({ loggedInUser }) {
  const [tripDetails, setTripDetails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [photoMap, setPhotoMap] = useState({});
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

        // Fetch photos for all locations
        const locations = response.data.map((trip) => ({
          stay_details: trip.stay_details,
        }));
        console.log("locations", locations);
        const photoResponse = await axios.post(
          `${import.meta.env.VITE_BACKEND_URL}get-photos-for-locations/`,
          { locations }
        );
        setPhotoMap(photoResponse.data);

        setLoading(false);
      } catch (error) {
        console.error("Error fetching trip details or photos:", error);
        setLoading(false);
      }
    }

    fetchTripDetails();
  }, [loggedInUser]);

  const handleViewClick = (tripId) => {
    navigate(`/plan/${tripId}`);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center pt-[300px] font-lato">
        <span className="loading loading-spinner loading-lg mr-5 text-custom-blue"></span>
        Loading trips..
      </div>
    );
  }

  return (
    <>
      <div className="pt-[80px] text-2xl md:text-3xl font-bold pl-4 md:pl-6">
        My Itineraries
      </div>
      <div className="text-sm md:text-sm pl-4 mt-2 md:pl-6">
        Lorem ipsum dolor sit amet consectetur adipisicing elit. Sint et tempore
        cumque quaerat sequi blanditiis facilis impedit fugiat.
      </div>
      <div className="flex flex-wrap justify-center md:justify-start gap-6 md:ml-[6rem] md:mt-5">
        {tripDetails.map((trip, index) => (
          <div
            key={index}
            className="w-full sm:w-1/2 md:w-1/3 p-4 max-w-xs"
          >
            <div className="card bg-[#0e1111] shadow-xl rounded-[40px] h-[400px] flex flex-col">
              <figure className="relative h-40">
                {photoMap[trip.stay_details] ? (
                  <img
                    src={`https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=${
                      photoMap[trip.stay_details]
                    }&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY}`}
                    alt="Trip"
                    className="w-full h-40 object-cover rounded-t-md"
                  />
                ) : (
                  <div className="flex items-center justify-center w-full h-40 bg-gray-300 rounded-t-md dark:bg-gray-700">
                    <svg
                      className="w-10 h-10 text-gray-200 dark:text-gray-600"
                      aria-hidden="true"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="currentColor"
                      viewBox="0 0 20 18"
                    >
                      <path d="M18 0H2a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2Zm-5.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3Zm4.376 10.481A1 1 0 0 1 16 15H4a1 1 0 0 1-.895-1.447l3.5-7A1 1 0 0 1 7.468 6a.965.965 0 0 1 .9.5l2.775 4.757 1.546-1.887a1 1 0 0 1 1.618.1l2.541 4a1 1 0 0 1 .028 1.011Z" />
                    </svg>
                  </div>
                )}
              </figure>
              
              <div className="card-body text-sm text-center">
              
                  <h2 className="card-title text-md font-lato mx-auto">
                    {trip.stay_details}
                  </h2>
                  <p className="font-lato text-custom-gray">
                    {trip.places_descriptions}
                  </p>
              
                <div className="card-actions justify-end mt-2">
                  <button
                    className="btn btn-active btn-link text-custom-gray text-md p-0"
                    onClick={() => handleViewClick(trip.trip_id)}
                  >
                    View Itinerary
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
