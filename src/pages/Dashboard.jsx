import { useState, useEffect } from "react";
import { Pie, Line } from "react-chartjs-2";
import "chart.js/auto";

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalDetections: 12450,
    imageDetections: 350,
    voiceDetections: 120,
    categories: {
      "ملابس غير لائقة": 30,
      "تنمر لفظي": 18,
      "محتوى مضلل": 20,
    },
    daily: [50, 120, 90, 300, 250, 180],
  });

  // مثال لتحديث الأرقام بشكل وهمي كل 10 ثواني (لتجربة الديناميكية)
  useEffect(() => {
    const interval = setInterval(() => {
      setStats((prev) => ({
        ...prev,
        totalDetections: prev.totalDetections + Math.floor(Math.random() * 5),
        imageDetections: prev.imageDetections + Math.floor(Math.random() * 2),
        voiceDetections: prev.voiceDetections + Math.floor(Math.random() * 2),
        daily: [...prev.daily.slice(1), Math.floor(Math.random() * 300)],
      }));
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // بيانات Pie
  const pieData = {
    labels: Object.keys(stats.categories),
    datasets: [
      {
        data: Object.values(stats.categories),
        backgroundColor: ["#006C35", "#e11d48", "#f59e0b"],
      },
    ],
  };

  // بيانات Line
  const lineData = {
    labels: ["اليوم1", "اليوم2", "اليوم3", "اليوم4", "اليوم5", "اليوم6"],
    datasets: [
      {
        label: "عدد المخالفات",
        data: stats.daily,
        borderColor: "#006C35",
        backgroundColor: "rgba(0,108,53,0.2)",
        tension: 0.3,
        fill: true,
      },
    ],
  };

  return (
    <section className="dashboard container">
      <h1 className="sadu-heading">📊 لوحة التحكم</h1>

      <div className="cards">
        <div className="card">
          <h3>إجمالي المخالفات</h3>
          <p>{stats.totalDetections.toLocaleString()}</p>
        </div>
        <div className="card">
          <h3>إشعارات بصرية</h3>
          <p>{stats.imageDetections}</p>
        </div>
        <div className="card">
          <h3>إشعارات صوتية</h3>
          <p>{stats.voiceDetections}</p>
        </div>
      </div>

      <div className="charts">
        <div className="chart pie-chart">
          <h3>توزيع المخالفات</h3>
          <Pie data={pieData} />
        </div>

        <div className="chart">
          <h3>المخالفات (آخر 6 أيام)</h3>
          <Line data={lineData} />
        </div>
      </div>
    </section>
  );
}
