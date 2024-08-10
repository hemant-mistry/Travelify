import React, { useState, useEffect } from "react";

const quotes = [
  "Travel is the healthiest addiction.",
  "Discovering new places is a way to discover more about yourself.",
  "There are no strangers here; only friends you haven’t yet met. – William Butler Yeats"
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
