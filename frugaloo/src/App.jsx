import Navbar from "./components/Navbar";
import PromptInput from "./components/PromptInput";

function App() {
  return (
    <>
      <Navbar />
      <div class="chat chat-start mt-5">
        <div class="chat-bubble">
          It's over Anakin,
          <br />I have the high ground.
        </div>
      </div>
      <div class="chat chat-end">
        <div class="chat-bubble">You underestimate my power!</div>
      </div>
      <PromptInput />
    </>
  );
}
export default App;
