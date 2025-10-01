import React from 'react'
import { Link } from 'react-router-dom'

export default function Home(){
  return (
    <section className="home">
      <div className="hero">
        <div className="hero-image">
          <img src="/assets/beacon.png" alt="منارة" />
        </div>
        <div className="hero-content">
          <h1 className="sadu-heading">كشف المخالفات في محتوى وسائل التواصل الاجتماعي</h1>
          <p>
            النظام يستخدم الذكاء الاصطناعي لمراقبة مقاطع الفيديو في الزمن الحقيقي
            واكتشاف مخالفات مثل التنمّر، الملابس غير اللائقة، استغلال الأطفال، والمعلومات المضللة.
          </p>
          <Link to="/realtime" className="cta">بدء الكشف في الوقت الفعلي</Link>
        </div>
      </div>

      <div className="sadu-strip"></div>

      <section className="features-row">
        <div className="feature-card">
          <div className="card-header"></div>
          <div className="card-body">
            <div className="title">
              <span className="icon">🛡️</span>
              <span>منظار</span>
            </div>
            <p>اكتشاف المخالفات البصرية باستخدام الرؤية الحاسوبية.</p>
          </div>
        </div>

        <div className="feature-card">
          <div className="card-header"></div>
          <div className="card-body">
            <div className="title">
              <span className="icon">🔍</span>
              <span>الـ NLP</span>
            </div>
            <p>تحليل النصوص والكلام لاكتشاف التنمّر والمعلومات المضللة.</p>
          </div>
        </div>

        <div className="feature-card">
          <div className="card-header"></div>
          <div className="card-body">
            <div className="title">
              <span className="icon">🎥</span>
              <span>بث مباشر</span>
            </div>
            <p>مراقبة اللحظة للحماية من المحتوى الضار في البثوص.</p>
          </div>
        </div>

      </section>
    </section>
  )
}
