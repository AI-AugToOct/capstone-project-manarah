import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();
  return (
    <section className="home">
      <div className="hero">
        <div className="hero-image">
          <img src="/assets/beacon.png" alt="منارة" />
        </div>
        <div className="hero-content">
          <h1 className="sadu-heading">
            كشف المخالفات في محتوى وسائل التواصل الاجتماعي
          </h1>
          <p>
            النظام يستخدم الذكاء الاصطناعي لمراقبة مقاطع الفيديو في الزمن الحقيقي
            واكتشاف مخالفات مثل التنمّر، الملابس غير اللائقة، استغلال الأطفال، والمعلومات المضللة.
          </p>
          
          {/* زر بدل الرابط */}
          <button className="cta" onClick={() => navigate("/realtime")}>
            بدء الكشف في الوقت الفعلي
          </button>
        </div>
      </div>

      <div className="sadu-strip"></div>

      <section className="features-row">
        <div className="feature-card">
          <div className="card-header"></div>
          <div className="card-body">
            <div className="title">
              <span>منظار</span>
              <span className="icon">🛡️</span>
            </div>
            <p>اكتشاف المخالفات البصرية باستخدام الرؤية الحاسوبية.</p>
          </div>
        </div>

        <div className="feature-card">
          <div className="card-header"></div>
          <div className="card-body">
            <div className="title">
              <span>الـ NLP</span>
              <span className="icon">🔍</span>
            </div>
            <p>تحليل النصوص والكلام لاكتشاف التنمّر والمعلومات المضللة.</p>
          </div>
        </div>

        <div className="feature-card">
          <div className="card-header"></div>
          <div className="card-body">
            <div className="title">
              <span>بث مباشر</span>
              <span className="icon">🎥</span>
            </div>
            <p>مراقبة اللحظة للحماية من المحتوى الضار في البثوث.</p>
          </div>
        </div>

      </section>
    </section>
  )
}
