import { useEffect, useState } from "react";

function App() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8001/api/health")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Backend unavailable");
        }

        return response.json();
      })
      .then(setHealth)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>Supply Prescript</h1>

      <p>
        Closed-Loop Prescriptive Analytics Platform for Supply Chain Risk
      </p>

      <hr />

      <h2>System Status</h2>

      {health && (
        <div>
          <strong>Backend:</strong> {health.status}
          <br />
          <strong>Service:</strong> {health.service}
          <br />
          <strong>Version:</strong> {health.version}
        </div>
      )}

      {error && (
        <p>
          <strong>Error:</strong> {error}
        </p>
      )}

      {!health && !error && <p>Connecting to backend...</p>}
    </div>
  );
}

export default App;