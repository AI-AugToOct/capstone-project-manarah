import React, { useState, useRef } from "react";

export default function AutoScan() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [contentId, setContentId] = useState(null);
  const videoRef = useRef(null);

  const onPick = (e) => {
    const f = e.target.files?.[0];
    setError("");
    setResult(null);
    setContentId(null);
    
    if (!f) return;
    
    // Accept both video and image
    if (!f.type.startsWith("video/") && !f.type.startsWith("image/")) {
      setError("الرجاء اختيار ملف فيديو أو صورة.");
      return;
    }
    
    setFile(f);
    const url = URL.createObjectURL(f);
    setPreviewUrl(url);
  };

  const analyze = async () => {
    if (!file) {
      setError("اختر ملف أولاً.");
      return;
    }
    
    setLoading(true);
    setError("");
    setResult(null);

    try {
      // Step 1: Upload content
      const fd = new FormData();
      fd.append("file", file);
      fd.append("user_id", "react_user");
      fd.append("caption", "تحليل من واجهة المستخدم");

      const uploadRes = await fetch("/api/v1/content/upload", {
        method: "POST",
        body: fd
      });

      if (!uploadRes.ok) {
        const errData = await uploadRes.json();
        throw new Error(errData.detail || "فشل رفع الملف");
      }

      const uploadData = await uploadRes.json();
      const cid = uploadData.content_id;
      setContentId(cid);

      // Step 2: Poll for results
      await pollForResults(cid);

    } catch (err) {
      setError(err.message || "حدث خطأ أثناء التحليل");
      setLoading(false);
    }
  };

  const pollForResults = async (cid) => {
    const maxAttempts = 60; // 60 attempts = 2 minutes max
    let attempts = 0;

    const checkStatus = async () => {
      try {
        const statusRes = await fetch(
          `/api/v1/content/${cid}/status?user_id=react_user`
        );

        if (!statusRes.ok) throw new Error("فشل التحقق من الحالة");

        const statusData = await statusRes.json();

        if (statusData.status === "completed") {
          // Get detailed results
          const detailsRes = await fetch(
            `/api/v1/content/${cid}/details?user_id=react_user`
          );

          if (!detailsRes.ok) throw new Error("فشل جلب النتائج");

          const details = await detailsRes.json();
          setResult(formatResults(details));
          setLoading(false);
          return;
        } else if (statusData.status === "failed") {
          throw new Error("فشل التحليل: " + (statusData.error || "خطأ غير معروف"));
        } else if (statusData.status === "processing") {
          attempts++;
          if (attempts >= maxAttempts) {
            throw new Error("انتهت مهلة التحليل");
          }
          // Poll again in 2 seconds
          setTimeout(checkStatus, 2000);
        }
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    checkStatus();
  };

  const formatResults = (details) => {
    const decision = details.decision;
    const visionAnalysis = details.analysis?.vision_analysis || {};
    const textAnalysis = details.analysis?.text_analysis || {};

    // Get primary violation
    const allViolations = [
      ...(visionAnalysis.violations || []),
      ...(textAnalysis.violations || [])
    ];

    const primaryViolation = allViolations[0] || {};

    // Map category to Arabic
    const categoryMap = {
      bullying: "التنمر والاستهزاء",
      child_exploitation: "استغلال الأطفال",
      worker_exploitation: "استغلال العاملين",
      vulgar_language: "الألفاظ المبتذلة",
      wealth_bragging: "التباهي بالأموال",
      tribal: "إثارة القبلية",
      sectarian: "إثارة الطائفية",
      racism: "العنصرية"
    };

    const actionMap = {
      auto_remove: "حذف تلقائي",
      human_review: "مراجعة بشرية",
      warning: "تحذير",
      allow: "مسموح"
    };

    return {
      id: details.content_id,
      ts: Date.now(),
      type_ar: categoryMap[primaryViolation.category] || "غير محدد",
      confidence: decision.combined_score,
      action: actionMap[decision.action] || decision.action,
      reason: decision.reasoning,
      visionScore: decision.vision_score,
      textScore: decision.text_score,
      violations: allViolations.map(v => ({
        category: categoryMap[v.category] || v.category,
        confidence: v.confidence,
        description: v.description || v.context
      }))
    };
  };

  return (
    <section className="autoscan container">
      <h1 className="sadu-heading" style={{ marginBottom: 8 }}>
        فحص تلقائي للمحتوى
      </h1>
      <p style={{ color: "var(--muted)", marginBottom: 20 }}>
        ارفع مقطع فيديو أو صورة لتحليل المحتوى واستخراج القرار النهائي.
      </p>

      {/* Upload Section */}
      <div className="upload-box">
        <input
          type="file"
          accept="video/*,image/*"
          onChange={onPick}
          id="uploadInput"
          hidden
        />
        <label htmlFor="uploadInput" className="upload-inner">
          <div className="big-icon">📤</div>
          <div>انقر لاختيار ملف أو اسحبه هنا</div>
          <div className="hint">MP4 / MOV / JPG / PNG</div>
        </label>

        {previewUrl && (
          <div className="preview">
            {file?.type.startsWith("video/") ? (
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
            ) : (
              <img
                src={previewUrl}
                alt="Preview"
                style={{
                  width: "100%",
                  borderRadius: "12px",
                  marginTop: "10px",
                }}
              />
            )}
          </div>
        )}

        <button
          className="cta-scan"
          onClick={analyze}
          disabled={loading || !file}
          style={{ marginTop: 20 }}
        >
          {loading ? "جاري التحليل... قد يستغرق دقيقة" : "بدء التحليل"}
        </button>

        {error && (
          <div className="error" style={{ color: "red", marginTop: 10 }}>
            ❌ {error}
          </div>
        )}
      </div>

      {/* Results Section */}
      {result && (
        <div className="decision-card">
          <h2>🔍 نتيجة التحليل</h2>
          
          <div className="decision-item">
            <span className="label">القرار:</span>
            <span className="value" style={{ 
              fontWeight: "bold",
              color: result.action === "حذف تلقائي" ? "#dc2626" :
                     result.action === "مراجعة بشرية" ? "#f59e0b" :
                     result.action === "تحذير" ? "#eab308" : "#10b981"
            }}>
              {result.action}
            </span>
          </div>

          <div className="decision-item">
            <span className="label">نوع المخالفة الرئيسي:</span>
            <span className="value">{result.type_ar}</span>
          </div>

          <div className="decision-item">
            <span className="label">درجة الثقة الإجمالية:</span>
            <span className="value">
              {(result.confidence * 100).toFixed(1)}%
            </span>
          </div>

          <div className="decision-item">
            <span className="label">درجة التحليل البصري:</span>
            <span className="value">
              {(result.visionScore * 100).toFixed(1)}%
            </span>
          </div>

          <div className="decision-item">
            <span className="label">درجة التحليل النصي:</span>
            <span className="value">
              {(result.textScore * 100).toFixed(1)}%
            </span>
          </div>

          <div className="decision-item">
            <span className="label">السبب:</span>
            <span className="value">{result.reason}</span>
          </div>

          {result.violations && result.violations.length > 0 && (
            <div style={{ marginTop: 20 }}>
              <h3>المخالفات المكتشفة:</h3>
              {result.violations.slice(0, 5).map((v, idx) => (
                <div key={idx} style={{ 
                  padding: 10, 
                  marginTop: 5, 
                  background: "#f3f4f6",
                  borderRadius: 8
                }}>
                  <strong>{v.category}</strong> - {(v.confidence * 100).toFixed(1)}%
                  <div style={{ fontSize: "0.9em", color: "#6b7280" }}>
                    {v.description}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}