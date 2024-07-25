import { Fragment, useEffect, useState } from "react";
import {
  GoogleMap,
  InfoWindowF,
  MarkerF,
  useLoadScript,
} from "@react-google-maps/api";
import axios from 'axios';  // Import axios for API calls
import { useParams } from "react-router-dom";

function Locate({ dayData = [] }) {  
  const { tripId, dayId } = useParams();
  const { isLoaded } = useLoadScript({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
  });

  const [activeMarker, setActiveMarker] = useState(null);
  const [inputValue, setInputValue] = useState('');
  const [localDayData, setLocalDayData] = useState(dayData);

  const handleActiveMarker = (marker) => {
    if (marker === activeMarker) {
      return;
    }
    setActiveMarker(marker);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    console.log(activeMarker);
    console.log(inputValue);
    try {
      // Make the API call
      await axios.post('https://your-api-endpoint.com/submit', {
        markerId: activeMarker,
        amountSpent: inputValue,
      });
      alert('Data submitted successfully!');
      setInputValue('');  // Clear the input field after successful submission
      setActiveMarker(null);  // Optionally close the InfoWindow
    } catch (error) {
      console.error('Error submitting data:', error);
      alert('Failed to submit data.');
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

  // Convert localDayData to markers
  const markers = (localDayData || []).map((data, index) => {
    const [lat, lng] = data.lat_long ? data.lat_long.split(',').map(coord => parseFloat(coord.trim())) : [0, 0];
    return {
      id: index,
      name: data.place_name || data.restaurant_name,
      position: { lat, lng },
    };
  });
  const mapOptions = {
    styles: [
     
      {
        "featureType": "administrative.country",
        "elementType": "labels",
        "stylers": [
          { "visibility": "on" }
        ]
      },
      {
        "featureType": "road",
        "elementType": "labels",
        "stylers": [
          { "visibility": "off" }
        ]
      },
      {
        featureType: "poi.business",
        elementType: "labels",
        stylers: [
          { visibility: "off" }
        ]
      },
      
      
      
    ],
    disableDefaultUI: true, // Disable default controls
    zoomControl: true,      // Enable zoom controls
    mapTypeControl: false,  // Disable map type control
    streetViewControl: false // Disable Street View control
  };
  return (
    <Fragment>
      <div className="container flex justify-center items-center h-screen md:h-[600px] lg:h-[800px]" style={{ margin: "auto", overflow: "hidden" }}>
        <div className="flex justify-center items-center h-full w-full" style={{ overflow: "hidden" }}>
          {isLoaded ? (
            <GoogleMap
              center={markers[0] ? markers[0].position : { lat: 40.3947365, lng: 49.6898045 }}
              zoom={10}
              onClick={() => setActiveMarker(null)}
              mapContainerStyle={{ height: "100%", width: "100%" }}
              options={mapOptions}
            >
              {markers.map(({ id, name, position }) => (
                <MarkerF
                  key={id}
                  position={position}
                  onClick={() => handleActiveMarker(name)}
                >
                  {activeMarker === name ? (
                    <InfoWindowF onCloseClick={() => setActiveMarker(null)}>
                      <form className="text-black flex flex-col p-2" onSubmit={handleSubmit}>
                        <p className="text-md mb-4 font-bold">{name}</p>
                        <input
                          type="text"
                          placeholder="Enter amount spent"
                          value={inputValue}
                          onChange={(e) => setInputValue(e.target.value)}
                          className="input input-sm input-bordered w-full max-w-xs bg-transparent"
                        />
                        <button type="submit" className="btn btn-sm btn-accent mt-5">
                          Submit
                        </button>
                      </form>
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
