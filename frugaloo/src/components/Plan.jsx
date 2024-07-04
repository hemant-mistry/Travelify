import googleMapIcon from "../assets/googleMapIcon.png";
import geminiIcon from "../assets/GeminiIcon.png";

function Plan() {
  return (
    <>
      <div className="text-center font-bold text-2xl lg:text-3xl">
        Your personalized <span className="text-primary">Itinerary..</span>
      </div>
      <div className="timeline-container p-10">
        <ul className="timeline timeline-snap-icon max-md:timeline-compact timeline-vertical bg-green">
          <li>
            <div className="timeline-middle">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="lightgreen"
                className="h-5 w-5"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="timeline-start mb-10 md:text-end">
              <time className="font-bold italic text-primary">Day 1</time>
              <div className="text-lg font-black">First Macintosh computer</div>
              The Apple Macintosh—later rebranded as the Macintosh 128K—is the
              original Apple Macintosh personal computer. It played a pivotal
              role in establishing desktop publishing as a general office
              function. The motherboard, a 9 in (23 cm) CRT monitor, and a
              floppy drive were housed in a beige case with integrated carrying
              handle; it came with a keyboard and single-button.
              <br />
              <div className="flex gap-2 mt-2 justify-end">
                {/* The button to open modal */}
                <label htmlFor="my_modal_7" className="btn btn-xs md:btn-sm">
                  <img src={geminiIcon} alt="Gemini Icon" className="h-6 w-6" />
                  Ask Gemini
                </label>

                {/* Put this part before </body> tag */}
                <input
                  type="checkbox"
                  id="my_modal_7"
                  className="modal-toggle"
                />
                <div className="modal " role="dialog">
                    
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
                  <label className="modal-backdrop" htmlFor="my_modal_7">
                    Close
                  </label>
                </div>
                <button className="btn btn-xs md:btn-sm">
                  <img
                    src={googleMapIcon}
                    alt="Google Map Icon"
                    className="h-6 w-6"
                  />
                  Locate
                </button>
                <button className="btn btn-success btn-xs md:btn-sm">
                  Mark as completed
                </button>
              </div>
            </div>
            <hr className="bg-green-500" />
          </li>
          <li>
            <hr />
            <div className="timeline-middle">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="h-5 w-5"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="timeline-end mb-10">
              <time className="font-bold italic text-primary">Day 2</time>
              <div className="text-lg font-black">iMac</div>
              iMac is a family of all-in-one Mac desktop computers designed and
              built by Apple Inc. It has been the primary part of Apples
              consumer desktop offerings since its debut in August 1998, and has
              evolved through seven distinct forms
            </div>
            <hr />
          </li>
          <li>
            <hr />
            <div className="timeline-middle">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="h-5 w-5"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="timeline-start mb-10 md:text-end">
              <time className="font-bold italic text-primary">Day 3</time>
              <div className="text-lg font-black">iPod</div>
              The iPod is a discontinued series of portable media players and
              multi-purpose mobile devices designed and marketed by Apple Inc.
              The first version was released on October 23, 2001, about 8+1⁄2
              months after the Macintosh version of iTunes was released. Apple
              sold an estimated 450 million iPod products as of 2022. Apple
              discontinued the iPod product line on May 10, 2022. At over 20
              years, the iPod brand is the oldest to be discontinued by Apple
            </div>
            <hr />
          </li>
          <li>
            <hr />
            <div className="timeline-middle">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="h-5 w-5"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="timeline-end mb-10">
              <time className="font-bold italic text-primary">Day 4</time>
              <div className="text-lg font-black">iPhone</div>
              iPhone is a line of smartphones produced by Apple Inc. that use
              Apples own iOS mobile operating system. The first-generation
              iPhone was announced by then-Apple CEO Steve Jobs on January 9,
              2007. Since then, Apple has annually released new iPhone models
              and iOS updates. As of November 1, 2018, more than 2.2 billion
              iPhones had been sold. As of 2022, the iPhone accounts for 15.6%
              of global smartphone market share
            </div>
            <hr />
          </li>
          <li>
            <hr />
            <div className="timeline-middle">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="h-5 w-5"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="timeline-start mb-10 md:text-end">
              <time className="font-bold italic text-primary">Day 5</time>
              <div className="text-lg font-black">Apple Watch</div>
              The Apple Watch is a line of smartwatches produced by Apple Inc.
              It incorporates fitness tracking, health-oriented capabilities,
              and wireless telecommunication, and integrates with iOS and other
              Apple products and services
            </div>
          </li>
          <li>
            <hr />
            <div className="timeline-middle">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="h-5 w-5"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="timeline-end mb-10">
              <time className="font-bold italic text-primary">Day 6</time>
              <div className="text-lg font-black">iPhone</div>
              iPhone is a line of smartphones produced by Apple Inc. that use
              Apples own iOS mobile operating system. The first-generation
              iPhone was announced by then-Apple CEO Steve Jobs on January 9,
              2007. Since then, Apple has annually released new iPhone models
              and iOS updates. As of November 1, 2018, more than 2.2 billion
              iPhones had been sold. As of 2022, the iPhone accounts for 15.6%
              of global smartphone market share
            </div>
            <hr />
          </li>
        </ul>
      </div>
    </>
  );
}

export default Plan;
