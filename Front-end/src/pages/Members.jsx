// src/pages.jsx
import React from "react";

export default function Members() {
  const team = [
    {
      name: "فيصل الفضيلي",
      position: "Full-Stack Engineer",
      photo: "/assets/faisal.jpg",
      linkedin: "https://www.linkedin.com/in/faisal-alfodialy"
    },
    {
      name: "عبدالله الأصقه",
      position: "AI/ML Engineer",
      photo: "/assets/abdullah.jpg",
      linkedin: "https://www.linkedin.com/in/abdullah-a-33465826a"
    },
    {
      name: "رايد الشمري",
      position: "AI/ML Engineer",
      photo: "/assets/raid.jpg",
      linkedin: "https://www.linkedin.com/in/rayid-al-shammari-337272293"
    },
    {
      name: "محمد اليمني",
      position: "AI/ML Engineer",
      photo: "/assets/mohammed.jpg",
      linkedin: "https://www.linkedin.com/in/mohammedalyamani-ai"
    }
  ];

  return (
    <section className="members">
      <h2 className="section-title">👥 فريق العمل</h2>
      <div className="members-grid">
        {team.map((member, index) => (
          <div className="member-card" key={index}>
            <img src={member.photo} alt={member.name} className="member-photo" />
            <h3>{member.name}</h3>
            <p>{member.position}</p>
            <a
              href={member.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="linkedin-link"
            >
              🔗 LinkedIn
            </a>
          </div>
        ))}
      </div>
    </section>
  );
}
