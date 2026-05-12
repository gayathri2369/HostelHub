import { useState } from "react";

function App() {
  const [message, setMessage] = useState("");

  const connectBackend = async () => {
    try {
      const response = await fetch(
        "https://hostelhub-jjvn.onrender.com/"
      );

      const data = await response.text();

      setMessage(data);
    } catch (error) {
      setMessage("Connection failed");
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
      <div className="bg-slate-900 p-10 rounded-3xl shadow-2xl w-[500px]">
        <h1 className="text-5xl font-bold text-cyan-400 mb-4">
          HostelHub
        </h1>

        <p className="text-slate-400 mb-8">
          Smart Hostel Management Platform
        </p>

        <button
          onClick={connectBackend}
          className="w-full bg-cyan-400 text-black p-4 rounded-2xl font-bold"
        >
          Connect Backend
        </button>

        <div className="mt-6 text-center text-xl">
          {message}
        </div>
      </div>
    </div>
  );
}

export default App;