import HeroImage from '../assets/NYC.png';


function Home() {
  return (
    <>
      <div
        className="hero min-h-screen fixed"
        style={{
          backgroundImage: `url(${HeroImage})`,

        }}
      >
        <div
          className="hero-overlay"
          style={{ backgroundColor: "rgba(0, 0, 0, 0.7)" }} // Adjust opacity as needed
        ></div>
        <div className="hero-content text-center " style={{ marginTop: '-10rem' }}>
          <div className="max-w-lg">
            <h1 className="mb-5 text-5xl font-bold text-white ">Welcome to Travelify</h1>
            <p className="mb-5 text-white">
              Provident cupiditate voluptatem et in. Quaerat fugiat ut assumenda
              excepturi exercitationem quasi. In deleniti eaque aut repudiandae
              et a.
            </p>
            <button className="btn btn-primary">Get Started</button>
          </div>
        </div>
      </div>
    </>
  );
}

export default Home;
