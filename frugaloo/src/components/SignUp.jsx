import { Link, useNavigate } from 'react-router-dom';  // Import useNavigate if using React Router v6

function SignUp() {
  // Initialize navigate hook
  const navigate = useNavigate();  // For React Router v6, use useNavigate()

  // Handle Login button click
  const handleLoginClick = () => {
    navigate('/login');  // Navigate to /login route
  };

  return (
    <>
      <div className="hero min-h-screen fixed">
        <div className="hero-content" style={{ marginTop: "-10rem" }}>
          <div className="card bg-base-100 md:w-96 sm:w-26 max-w-sm sm:w-[25] shadow-2xl">
            <form className="card-body">
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Email</span>
                </label>
                <input
                  type="email"
                  placeholder="email"
                  className="input input-bordered input-sm"
                  required
                />
              </div>
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Password</span>
                </label>
                <input
                  type="password"
                  placeholder="password"
                  className="input input-bordered input-sm"
                  required
                />
              </div>
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Confirm Password</span>
                </label>
                <input
                  type="password"
                  placeholder="re-type password"
                  className="input input-bordered input-sm"
                  required
                />
              </div>
              <div className="card-actions justify-center mt-5">
                <button className="btn btn-ghost btn-sm" onClick={handleLoginClick}>Login</button>
                <button className="btn btn-primary btn-sm">Sign Up</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}

export default SignUp;
