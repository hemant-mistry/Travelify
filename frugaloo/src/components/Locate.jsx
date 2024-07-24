import React, { useState, useEffect } from 'react';
import { useJsApiLoader, GoogleMap, Marker, DirectionsService, DirectionsRenderer } from '@react-google-maps/api';

const center = { lat: 48.8584, lng: 2.2945 };

const Locate = () => {
  const [waypoints, setWaypoints] = useState([
    { lat: 48.8584, lng: 2.2945 },
    { lat: 48.8606, lng: 2.3376 },
    { lat: 48.8606, lng: 2.3276 }
  ]);
  const [directionsResponse, setDirectionsResponse] = useState(null);

  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    libraries: ['places'] // Include libraries if needed
  });

  useEffect(() => {
    if (isLoaded && waypoints.length > 1) {
      const directionsService = new window.google.maps.DirectionsService();

      directionsService.route(
        {
          origin: waypoints[0],
          destination: waypoints[waypoints.length - 1],
          waypoints: waypoints.slice(1, -1).map(point => ({ location: point, stopover: true })),
          travelMode: window.google.maps.TravelMode.DRIVING
        },
        (result, status) => {
          if (status === window.google.maps.DirectionsStatus.OK) {
            setDirectionsResponse(result);
          } else {
            console.error(`Directions request failed due to ${status}`);
          }
        }
      );
    }
  }, [isLoaded, waypoints]);

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

  return isLoaded ? (
    <GoogleMap
      center={center}
      zoom={15}
      mapContainerStyle={{width:"400px%", height:"847px"}}
      options={mapOptions}
    >
      {waypoints.map((waypoint, index) => (
        <Marker
          key={index}
          position={{ lat: waypoint.lat, lng: waypoint.lng }}
        />
      ))}
      {directionsResponse && (
        <DirectionsRenderer
          directions={directionsResponse}
          options={{
            polylineOptions: {
              strokeColor: "#7743DB",
              strokeOpacity: 1.0,
              strokeWeight: 10,
            }
          }}
        />
      )}
    </GoogleMap>
  ) : (
    <></>
  );
};

export default Locate;
