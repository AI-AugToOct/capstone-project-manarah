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
    
    console.log('✅ File selected:', {
      name: f.name,
      size: f.size,
      type: f.type
    });
    
    setFile(f);
    const url = URL.createObjectURL(f);
    setPreviewUrl(url);
  };

  const analyze = async () => {
    console.log('🔵 Analyze button clicked');

    if (!file) {
      console.log('❌ No file selected');
      setError("اختر ملف أولاً.");
      return;
    }

    console.log('✅ File selected:', file.name, 'Size:', file.size, 'Type:', file.type);

    setLoading(true);
    setError("");
    setResult(null);

    try {
      // Step 1: Upload content
      const fd = new FormData();
      fd.append("file", file);
      fd.append("user_id", "react_user");
      fd.append("caption", "تحليل من واجهة المستخدم");

      console.log('📤 Starting upload to /api/v1/content/upload');

      const uploadRes = await fetch("/api/v1/content/upload", {
        method: "POST",
        body: fd
        // Don't set Content-Type - browser sets it with boundary
      });

      console.log('📥 Upload response status:', uploadRes.status);

      if (!uploadRes.ok) {
        const errorText = await uploadRes.text();
        console.error('❌ Upload failed. Status:', uploadRes.status, 'Error:', errorText);
        try {
          const errData = JSON.parse(errorText);
          throw new Error(errData.detail || "فشل رفع الملف");
        } catch (parseErr) {
          throw new Error(`فشل رفع الملف (${uploadRes.status}): ${errorText}`);
        }
      }

      const uploadData = await uploadRes.json();
      const cid = uploadData.content_id;
      console.log('✅ Content uploaded successfully! ID:', cid);
      setContentId(cid);

      // Step 2: Poll for results
      console.log('🔄 Starting to poll for results...');
      await pollForResults(cid);

    } catch (err) {
      console.error('❌ Critical error in analyze():', err);
      console.error('Error stack:', err.stack);
      setError(err.message || "حدث خطأ أثناء التحليل");
      setLoading(false);
    }
  };

  const pollForResults = async (cid) => {
    const maxAttempts = 60; // 60 attempts = 2 minutes max
    let attempts = 0;

    const checkStatus = async () => {
      try {
        console.log(`🔄 Polling attempt ${attempts + 1}/${maxAttempts}`);
        
        const statusRes = await fetch(
          `/api/v1/content/${cid}/status?user_id=react_user`
        );

        if (!statusRes.ok) {
          const errorText = await statusRes.text();
          console.error('❌ Status check failed:', errorText);
          throw new Error("فشل التحقق من الحالة");
        }

        const statusData = await statusRes.json();
        console.log('📊 Status:', statusData.status);

        if (statusData.status === "completed") {
          console.log('✅ Analysis completed!');
          console.log('📋 Analysis results:', statusData);
          setResult(formatResults(statusData));
          setLoading(false);
          return;
          
        } else if (statusData.status === "failed") {
          console.error('❌ Analysis failed:', statusData.error);
          throw new Error("فشل التحليل: " + (statusData.error || "خطأ غير معروف"));
          
        } else if (statusData.status === "processing") {
          attempts++;
          if (attempts >= maxAttempts) {
            console.error('⏱️ Timeout reached');
            throw new Error("انتهت مهلة الانتظار. يرجى المحاولة لاحقاً");
          }
          // Poll again in 2 seconds
          setTimeout(checkStatus, 2000);
        }
      } catch (err) {
        console.error('❌ Polling error:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    checkStatus();
  };

  const formatResults = (statusData) => {
    console.log('🔧 Formatting results:', statusData);

    // Map category to Arabic
    const categoryMap = {
      bullying: "التنمر والاستهزاء",
      child_exploitation: "استغلال الأطفال",
      worker_exploitation: "استغلال العاملين",
      vulgar_language: "الألفاظ المبتذلة",
      wealth_bragging: "التباهي بالأموال",
      tribal: "إثارة القبلية",
      sectarian: "إثارة الطائفية",
      racism: "العنصرية",
      none: "لا توجد مخالفات"
    };

    const actionMap = {
      auto_remove: "حذف تلقائي",
      human_review: "مراجعة بشرية",
      warning: "تحذير",
      allow: "مسموح"
    };

    const formatted = {
      id: statusData.content_id,
      ts: Date.now(),
      type_ar: categoryMap[statusData.main_violation_type] || statusData.main_violation_type,
      confidence: statusData.overall_confidence_score / 100,
      action: actionMap[statusData.decision] || statusData.decision || "غير محدد",
      reason: statusData.reason || "لا يوجد سبب",
      visionScore: statusData.vision_analysis_score / 100,
      textScore: statusData.audio_analysis_score / 100,
      totalViolations: statusData.main_violation_type === "none" ? 0 : 1
    };

    console.log('✅ Formatted results:', formatted);
    return formatted;
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
            <span className="label">عدد المخالفات المكتشفة:</span>
            <span className="value" style={{ 
              fontWeight: "bold",
              color: result.totalViolations > 0 ? "#dc2626" : "#10b981"
            }}>
              {result.totalViolations}
            </span>
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
        </div>
      )}
    </section>
  );
}