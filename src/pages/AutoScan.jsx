import React, { useState, useRef } from "react";

export default function AutoScan() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const videoRef = useRef(null);

  const onPick = (e) => {
    const f = e.target.files?.[0];
    setError("");
    setResult(null);
    if (!f) return;
    if (!f.type.startsWith("video/")) {
      setError("الرجاء اختيار ملف فيديو.");
      return;
    }
    setFile(f);
    const url = URL.createObjectURL(f);
    setPreviewUrl(url);
  };

  const analyze = async () => {
    if (!file) {
      setError("اختر فيديو أولاً.");
      return;
    }
    setLoading(true);
    setError("");

    try {
      const fd = new FormData();
      fd.append("file", file);

      const res = await fetch("/api/analyze", { method: "POST", body: fd });

      if (!res.ok) throw new Error("backend unreachable");
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult(makeLocalMock());
    } finally {
      setLoading(false);
    }
  };

  // ✅ نتائج تجريبية بسيطة
  function makeLocalMock() {
    const types = [
      "استغلال الأطفال كمحتوى",
      "الألفاظ المبتذلة",
      "التباهي بالأموال أو الممتلكات",
      "إثارة القبلية أو العنصرية أو الطائفية",
      "كشف الجسد من الكتفين حتى الساقين",
      "التنمر أو الاستهزاء بالآخرين",
    ];

    const type = types[Math.floor(Math.random() * types.length)];
    const confidence = +(0.6 + Math.random() * 0.4).toFixed(2);
    const reason =
      confidence > 0.8
        ? "تم اكتشاف مؤشرات واضحة تدل على مخالفة في المحتوى"
        : "هناك مؤشرات ضعيفة تشير لاحتمالية وجود مخالفة";

    return {
      id: Date.now(),
      ts: Date.now(),
      type_ar: type,
      confidence,
      reason,
      notes: "✅ نتائج تجريبية — لعدم توفر النموذج الفعلي حالياً.",
    };
  }

  return (
    <section className="autoscan container">
      <h1 className="sadu-heading" style={{ marginBottom: 8 }}>
        فحص تلقائي للمحتوى
      </h1>
      <p style={{ color: "var(--muted)", marginBottom: 20 }}>
        ارفع مقطع فيديو لتحليل الصورة والصوت واستخراج القرار النهائي.
      </p>

      {/* Upload Section */}
      <div className="upload-box">
        <input
          type="file"
          accept="video/*"
          onChange={onPick}
          id="uploadInput"
          hidden
        />
        <label htmlFor="uploadInput" className="upload-inner">
          <div className="big-icon">📤</div>
          <div>انقر لاختيار فيديو أو اسحبه هنا</div>
          <div className="hint">MP4 / MOV / WEBM</div>
        </label>

        {previewUrl && (
          <div className="preview">
            <video
              ref={videoRef}
              src={previewUrl}
              controls
              className="video"
              style={{
                width: "100%",
                borderRadius: "12px",
                marginTop: "10px",
              }}
            />
          </div>
        )}

        <button
          className="cta-scan"
          onClick={analyze}
          disabled={loading || !file}
          style={{ marginTop: 20 }}
        >
          {loading ? "جاري التحليل..." : "بدء التحليل"}
        </button>

        {error && <div className="error">{error}</div>}
      </div>

      {/* ✅ النتيجة النهائية */}
      {result && (
        <div className="decision-card">
          <h2>🔍 نتيجة التحليل</h2>
          <div className="decision-item">
            <span className="label">نوع المخالفة:</span>
            <span className="value">{result.type_ar}</span>
          </div>
          <div className="decision-item">
            <span className="label">دقّة النموذج:</span>
            <span className="value">
              {(result.confidence * 100).toFixed(1)}%
            </span>
          </div>
          <div className="decision-item">
            <span className="label">السبب:</span>
            <span className="value">{result.reason}</span>
          </div>
          <p className="foot-note">{result.notes}</p>
        </div>
      )}
    </section>
  );
}
