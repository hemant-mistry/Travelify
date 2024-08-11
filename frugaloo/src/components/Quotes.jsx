import React, { useState, useEffect } from "react";

const quotes = [
 "Hang on tight, your journey is about to get even better!",
"Gemini's sifting through your preferences to craft the perfect itinerary.",
"Adjusting your travel plans—this is where the magic happens.",
"We’re fine-tuning the details to make your trip unforgettable.",
"Gemini’s mapping out the best routes for your adventure.",
"Hold tight—your ideal itinerary is almost ready!",
"Adding a dash of excitement to your travel plans. Just a bit longer!",
"Gemini’s working behind the scenes to create something special.",
"Fine-tuning those final touches for the ultimate experience.",
"Your journey is about to get a serious upgrade. Stay tuned!",
"Gemini’s sorting out the best options for your perfect trip.",
"Almost there! Your personalized itinerary is just moments away.",
"Your adventure is getting an extra layer of awesomeness.",
"Hang tight—Gemini’s adding some surprises to your itinerary!",
"We’re making sure every detail is just right for your trip.",
"Just a few more tweaks and your adventure will be set.",
"Gemini’s cooking up something truly unforgettable for you.",
"Almost done! Your custom travel plans are nearly ready.",
"Your perfect trip is just around the corner. Almost there!"
];

const QuoteComponent = () => {
  const [currentQuote, setCurrentQuote] = useState(quotes[0]);

  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentQuote((prevQuote) => {
        // Pick a random quote different from the previous one
        let newQuote;
        do {
          newQuote = quotes[Math.floor(Math.random() * quotes.length)];
        } while (newQuote === prevQuote);
        return newQuote;
      });
    }, 1000);

    // Cleanup the interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="flex justify-center items-center text-primary gap-2">
      <div className="quote-box">{currentQuote}</div>
    </div>
  );
};

export default QuoteComponent;
