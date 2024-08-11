import React from "react";

function Finance() {
  return (
    <div className="container mx-auto p-6 pt-[80px]">

      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">General Questions</h2>
        <div className="collapse collapse-arrow border border-base-300 bg-base-100 rounded-box mb-2">
          <input type="checkbox" className="peer" />
          <div className="collapse-title text-md font-medium">
            What is Travelify?
          </div>
          <div className="collapse-content">
            <p>
              Travelify is a Gemini-powered itinerary planner that helps you
              create personalized travel itineraries based on your preferences,
              budget, and travel dates. The app provides tools to customize and
              organize your trip, ensuring a seamless travel experience.
            </p>
          </div>
        </div>

        <div className="collapse collapse-arrow border border-base-300 bg-base-100 rounded-box mb-2">
          <input type="checkbox" className="peer" />
          <div className="collapse-title text-md font-medium">
            How do I sign up for Travelify?
          </div>
          <div className="collapse-content">
            <p>
              You can sign up for Travelify using your Google account or by
              creating an account with your email. Simply follow the prompts on
              the app to complete your registration.
            </p>
          </div>
        </div>

        <div className="collapse collapse-arrow border border-base-300 bg-base-100 rounded-box mb-2">
          <input type="checkbox" className="peer" />
          <div className="collapse-title text-md font-medium">
            Is Travelify free to use?
          </div>
          <div className="collapse-content">
            <p>
              Travelify is currently free to use, although it’s still under
              development.
            </p>
          </div>
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Itinerary Planning</h2>
        <div className="collapse collapse-arrow border border-base-300 bg-base-100 rounded-box mb-2">
          <input type="checkbox" className="peer" />
          <div className="collapse-title text-md font-medium">
            How do I select a destination and plan my itinerary?
          </div>
          <div className="collapse-content">
            <p>
              Enter your desired destination in the search bar and choose your
              travel dates and duration. You can then set your budget and avatar
              preferences to organize your trip accordingly.
            </p>
          </div>
        </div>

        <div className="collapse collapse-arrow border border-base-300 bg-base-100 rounded-box mb-2">
          <input type="checkbox" className="peer" />
          <div className="collapse-title text-md font-medium">
            Can I customize my itinerary?
          </div>
          <div className="collapse-content">
            <p>
              Absolutely! You can add, change, or remove activities from your
              itinerary at any time. Travelify provides the tools to help you
              tailor your trip to your liking.
            </p>
          </div>
        </div>

        <div className="collapse collapse-arrow border border-base-300 bg-base-100 rounded-box mb-2">
          <input type="checkbox" className="peer" />
          <div className="collapse-title text-md font-medium">
            How do I manage my budget while planning?
          </div>
          <div className="collapse-content">
            <p>
              When setting up your itinerary, select your budget range.
              Travelify will help you organize your trip according to your
              financial plan, ensuring that all activities and accommodations
              fit within your specified budget.
            </p>
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Using Gemini AI</h2>
        <div className="collapse collapse-arrow border border-base-300 bg-base-100 rounded-box mb-2">
          <input type="checkbox" className="peer" />
          <div className="collapse-title text-md font-medium">
            What is Gemini AI, and how does it help me?
          </div>
          <div className="collapse-content">
            <p>
              Gemini AI assists you in customizing and organizing your travel
              plans. It helps you tailor your itinerary based on ever-changing
              moods and preferences.
            </p>
          </div>
        </div>

        <div className="collapse collapse-arrow border border-base-300 bg-base-100 rounded-box mb-2">
          <input type="checkbox" className="peer" />
          <div className="collapse-title text-md font-medium">
            How do I use Gemini AI for my travel planning?
          </div>
          <div className="collapse-content">
            <p>
              You can use the "Ask Gemini AI" feature in the app to make
              adjustments to your itinerary, such as adding, changing, or
              removing activities, and to receive tailored options based on your
              preferences.
            </p>
          </div>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">
          Data Privacy and Security
        </h2>
        <div className="collapse collapse-arrow border border-base-300 bg-base-100 rounded-box mb-2">
          <input type="checkbox" className="peer" />
          <div className="collapse-title text-md font-medium">
            How does Travelify protect my personal information?
          </div>
          <div className="collapse-content">
            <p>
              We take your privacy and security seriously. Travelify adheres to
              strict data protection policies and complies with relevant
              regulations to ensure your personal information is secure. Please
              refer to our Privacy Policy for more details.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Finance;
