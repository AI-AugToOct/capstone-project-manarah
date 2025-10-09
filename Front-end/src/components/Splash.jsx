import { useEffect, useState } from "react";

export default function Splash({ children }) {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1800); // ثانيتين
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="splash-screen">
        <img src="/assets/icon1.png" alt="Logo" className="splash-logo" />
      </div>
    );
  }

  return children;
}
