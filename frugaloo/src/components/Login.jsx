import { Link, useNavigate } from 'react-router-dom';  // Import useNavigate if using React Router v6

function Login() {
  // Initialize navigate hook
  const navigate = useNavigate();  // For React Router v6, use useNavigate()

  // Handle SignUp button click
  const handleSignUpClick = () => {
    navigate('/signup');  // Navigate to /signup route
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
                <label className="label">
                  <a href="#" className="label-text-alt link link-hover">
                    Forgot password?
                  </a>
                </label>
              </div>
              <div className="card-actions justify-center">
                <button className="btn btn-primary btn-sm">Login</button>
                <button className="btn btn-ghost btn-sm" onClick={handleSignUpClick}>Sign Up</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}

export default Login;
