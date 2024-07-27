import { Fragment, useEffect, useState, useMemo } from "react";
import {
  GoogleMap,
  InfoWindowF,
  MarkerF,
  useLoadScript,
} from "@react-google-maps/api";
import axios from "axios";
import { useParams } from "react-router-dom";
import shopIcon from "../assets/shopIcon.png";
import restoIcon from "../assets/restoIcon.png";
import othersIcon from "../assets/othersIcon.png";
import moneyIcon from "../assets/moneyIcon.png";
import Lottie from "react-lottie";
import animationData from "../assets/lotties/submitted.json";

function Locate({ dayData = [], loggedInUser }) {
  const { tripId, dayId } = useParams();
  const { isLoaded } = useLoadScript({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
  });

  const [activeMarker, setActiveMarker] = useState(null);
  const [inputValue, setInputValue] = useState(0);
  const [localDayData, setLocalDayData] = useState(dayData);
  const [mapCenter, setMapCenter] = useState({
    lat: 40.3947365,
    lng: 49.6898045,
  });
  const [selectedCategory, setSelectedCategory] = useState("");
  const [showSuccessAnimation, setShowSuccessAnimation] = useState(false);
  const [formSubmitting, setFormSubmitting] = useState(false);

  const handleActiveMarker = (marker, position) => {
    if (marker === activeMarker) {
      return;
    }
    setActiveMarker(marker);
    setMapCenter(position);
  };

  const handleRadioChange = (event) => {
    setSelectedCategory(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFormSubmitting(true);

    try {
      await axios.post(`${import.meta.env.VITE_BACKEND_URL}add-finance-log/`, {
        user_id: loggedInUser.id,
        trip_id: tripId,
        amount: inputValue,
        place: activeMarker,
        category: selectedCategory,
        day: dayId,
      });

      setShowSuccessAnimation(true);
      setInputValue("");
      setSelectedCategory("");

      setTimeout(() => {
        setShowSuccessAnimation(false);
        setFormSubmitting(false);
      }, 3000);
    } catch (error) {
      console.error("Error submitting data:", error);
      alert("Failed to submit data.");
      setFormSubmitting(false);
    }
  };

  useEffect(() => {
    const storageKey = `${tripId}-${dayId}`;
    const storedData = localStorage.getItem(storageKey);

    if (storedData) {
      setLocalDayData(JSON.parse(storedData));
    } else if (dayData.length) {
      localStorage.setItem(storageKey, JSON.stringify(dayData));
      setLocalDayData(dayData);
    }
  }, [dayData, tripId, dayId]);

  const markers = useMemo(() => {
    return (localDayData || []).map((data, index) => {
      const [lat, lng] = data.lat_long
        ? data.lat_long.split(",").map((coord) => parseFloat(coord.trim()))
        : [0, 0];
      return {
        id: index,
        name: data.place_name || data.restaurant_name,
        position: { lat, lng },
        description: data.description,
      };
    });
  }, [localDayData]);

  useEffect(() => {
    if (markers.length > 0) {
      setMapCenter(markers[0].position);
    }
  }, [markers]);

  const mapOptions = {
    styles: [
      {
        featureType: "administrative.country",
        elementType: "labels",
        stylers: [{ visibility: "on" }],
      },
      {
        featureType: "road",
        elementType: "labels",
        stylers: [{ visibility: "off" }],
      },
      {
        featureType: "poi.business",
        elementType: "labels",
        stylers: [{ visibility: "off" }],
      },
    ],
    disableDefaultUI: true,
    zoomControl: true,
    mapTypeControl: false,
    streetViewControl: false,
    scrollwheel: true,
  };

  return (
    <Fragment>
      <div
        className="container flex justify-center items-center h-screen md:h-[600px] lg:h-[800px]"
        style={{ margin: "auto", overflow: "hidden" }}
      >
        <div
          className="flex justify-center items-center h-full w-full"
          style={{ overflow: "hidden" }}
        >
          {isLoaded ? (
            <GoogleMap
              center={mapCenter}
              zoom={10}
              onClick={() => setActiveMarker(null)}
              mapContainerStyle={{ height: "100%", width: "100%" }}
              options={mapOptions}
            >
              {markers.map(({ id, name, position, description }) => (
                <MarkerF
                  key={id}
                  position={position}
                  onClick={() => handleActiveMarker(name, position)}
                >
                  {activeMarker === name ? (
                    <InfoWindowF onCloseClick={() => setActiveMarker(null)}>
                      {showSuccessAnimation ? (
                        <div className="text-center flex flex-col p-2 max-w-sm">
                          <Lottie
                            options={{
                              loop: false,
                              autoplay: true,
                              animationData: animationData,
                            }}
                            height={50}
                            width={50}
                          />
                          <p className="mt-2 text-green-600">
                            Submitted successfully!
                          </p>
                        </div>
                      ) : (
                        <form
                          className="text-black flex flex-col p-2 max-w-sm"
                          onSubmit={handleSubmit}
                        >
                          <p className="card-title text-md mb-4 font-bold">
                            {name}
                            <div className="badge badge-error">Rush</div>
                          </p>

                          <p className="text-md font-normal">{description}</p>

                          <div className="flex flex-row gap-2 mt-5">
                            <label className="flex items-center">
                              <input
                                type="radio"
                                value="Shopping"
                                checked={selectedCategory === "Shopping"}
                                onChange={handleRadioChange}
                                className="hidden"
                              />
                              <div
                                className={`flex items-center justify-center w-10 h-10 rounded-full cursor-pointer ${
                                  selectedCategory === "Shopping"
                                    ? "bg-blue-200"
                                    : "bg-gray-200"
                                }`}
                              >
                                <img
                                  src={shopIcon}
                                  alt="Shopping"
                                  className="w-6 h-6"
                                />
                              </div>
                              <span className="ml-2">Shopping</span>
                            </label>
                            <label className="flex items-center">
                              <input
                                type="radio"
                                value="Restaurant"
                                checked={selectedCategory === "Restaurant"}
                                onChange={handleRadioChange}
                                className="hidden"
                              />
                              <div
                                className={`flex items-center justify-center w-10 h-10 rounded-full cursor-pointer ${
                                  selectedCategory === "Restaurant"
                                    ? "bg-blue-200"
                                    : "bg-gray-200"
                                }`}
                              >
                                <img
                                  src={restoIcon}
                                  alt="Category 2"
                                  className="w-6 h-6"
                                />
                              </div>
                              <span className="ml-2">Restaurant</span>
                            </label>
                            <label className="flex items-center">
                              <input
                                type="radio"
                                value="Others"
                                checked={selectedCategory === "Others"}
                                onChange={handleRadioChange}
                                className="hidden"
                              />
                              <div
                                className={`flex items-center justify-center w-10 h-10 rounded-full cursor-pointer ${
                                  selectedCategory === "Others"
                                    ? "bg-blue-200"
                                    : "bg-gray-200"
                                }`}
                              >
                                <img
                                  src={othersIcon}
                                  alt="Category 3"
                                  className="w-6 h-6"
                                />
                              </div>
                              <span className="ml-2">Others</span>
                            </label>
                          </div>
                          <label className="input input-bordered bg-transparent flex items-center gap-2 mt-5">
                            <img
                              src={moneyIcon}
                              alt="Amount"
                              className="h-6 w-6 opacity-70"
                            />
                            <input
                              type="number"
                              placeholder="Enter amount spent"
                              value={inputValue}
                              onChange={(e) => setInputValue(e.target.value)}
                              className="grow input input-sm bg-transparent appearance-none"
                            />
                          </label>
                          <button
                            type="submit"
                            className="btn btn-sm bg-blue-200 text-black border-none hover:bg-blue-300 mt-5 max-w-sm mx-auto"
                            disabled={formSubmitting}
                          >
                            {formSubmitting ? "Submitting..." : "Submit"}
                          </button>
                        </form>
                      )}
                    </InfoWindowF>
                  ) : null}
                </MarkerF>
              ))}
            </GoogleMap>
          ) : null}
        </div>
      </div>
    </Fragment>
  );
}

export default Locate;
