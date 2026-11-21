import { useEffect, useState } from "react";
import api from "../api";

// Free hosting puts the API to sleep. If the first call is slow, tell the visitor why.
export default function ServerWakeBanner() {
  const [waking, setWaking] = useState(false);

  useEffect(() => {
    let finished = false;
    const timer = setTimeout(() => {
      if (!finished) setWaking(true);
    }, 2500);

    api
      .get("/api/health", { timeout: 90000 })
      .catch(() => {})
      .finally(() => {
        finished = true;
        clearTimeout(timer);
        setWaking(false);
      });

    return () => {
      finished = true;
      clearTimeout(timer);
    };
  }, []);

  if (!waking) return null;

  return (
    <div className="wake-banner">
      Waking up the server. This app runs on free hosting that sleeps when idle, so the first
      load can take up to a minute. Please wait.
    </div>
  );
}