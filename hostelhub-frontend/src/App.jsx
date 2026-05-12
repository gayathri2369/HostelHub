import API_URL from "./api"

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">

      <div className="p-10">

        <h1 className="text-5xl font-bold text-cyan-400">
          HostelHub
        </h1>

        <p className="mt-4 text-gray-300 text-xl">
          Smart Hostel Management Platform
        </p>

        <div className="mt-10 grid md:grid-cols-2 gap-10">

          <div className="bg-slate-900 p-8 rounded-3xl shadow-2xl">

            <h2 className="text-3xl font-bold mb-6">
              Student Login
            </h2>

            <input
              type="email"
              placeholder="Enter Email"
              className="w-full p-4 rounded-xl bg-slate-800 mb-4"
            />

            <input
              type="password"
              placeholder="Enter Password"
              className="w-full p-4 rounded-xl bg-slate-800 mb-4"
            />

            <button
              onClick={async () => {
                try {
                  const response = await fetch(API_URL)

                  if (response.ok) {
                    alert("Backend Connected Successfully")
                  } else {
                    alert("Backend Error")
                  }
                } catch (error) {
                  alert("Connection Failed")
                }
              }}
              className="w-full bg-cyan-400 text-black p-4 rounded-xl font-bold hover:bg-cyan-300"
            >
              Connect Backend
            </button>

          </div>

          <div className="bg-slate-900 p-8 rounded-3xl shadow-2xl">

            <h2 className="text-3xl font-bold mb-6">
              Features
            </h2>

            <ul className="space-y-4 text-lg">
              <li>✅ Room Management</li>
              <li>✅ Attendance Tracking</li>
              <li>✅ Fee Management</li>
              <li>✅ Complaint System</li>
              <li>✅ Student Dashboard</li>
              <li>✅ Admin Dashboard</li>
            </ul>

          </div>

        </div>

      </div>

    </div>
  )
}

export default App