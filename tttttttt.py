import cv2
from ultralytics import YOLO

# ----------------------------------------------------------------------------------
# 💡 الخطوة 1: حدد إعدادات التشغيل
# ----------------------------------------------------------------------------------

# ⚠️ غير هذا المسار للتبديل بين الصيغتين (.pt) أو (.onnx)
# 1. استخدم مسار PyTorch:
MODEL_PATH = "/Users/rayidalshammari/Desktop/late fuiosn/models/Child_Detection_Model.pt"  
# 2. أو استخدم مسار ONNX:
# MODEL_PATH = "path/to/your/best.onnx"

# مؤشر الكاميرا: 0 هو الافتراضي. إذا لم يعمل، جرب 1 أو 2.
CAMERA_INDEX = 0 
# حد أدنى للثقة (Confidence) لعرض الكشف
CONF_THRESHOLD = 0.5 

# ----------------------------------------------------------------------------------
# 💡 الخطوة 2: تهيئة النموذج والكاميرا
# ----------------------------------------------------------------------------------

try:
    # تحميل النموذج
    model = YOLO(MODEL_PATH)

    # فتح الكاميرا
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise IOError(f"❌ لا يمكن فتح الكاميرا بالرقم {CAMERA_INDEX}. يرجى التحقق من التوصيل.")
        
    print(f"✅ تم تحميل النموذج: {MODEL_PATH}")
    print("🎥 بدأ بث الكاميرا. اضغط 'q' للإيقاف.")

except Exception as e:
    print(f"❌ حدث خطأ أثناء التحميل: {e}")
    exit()

# ----------------------------------------------------------------------------------
# 💡 الخطوة 3: حلقة الكشف في الوقت الفعلي
# ----------------------------------------------------------------------------------

while True:
    # قراءة إطار (Frame) من الكاميرا
    ret, frame = cap.read()
    if not ret:
        print("⚠️ فشل في قراءة الإطار من الكاميرا.")
        break

    # إجراء الكشف باستخدام النموذج
    # box=True: يرسم صناديق الكشف
    # conf=CONF_THRESHOLD: يطبق حد الثقة
    results = model.predict(
        source=frame, 
        conf=CONF_THRESHOLD, 
        verbose=False # لإخفاء رسائل التوقع (Prediction messages)
    )

    # عرض الإطار مع نتائج الكشف (الإطار يكون مرسوماً تلقائياً بواسطة YOLO)
    # ملاحظة: results[0].plot() هو وظيفة Ultralytics التي ترسم على الإطار
    annotated_frame = results[0].plot()
    
    cv2.imshow("YOLO Real-Time Detection (Press 'q' to exit)", annotated_frame)

    # الخروج عند الضغط على 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ----------------------------------------------------------------------------------
# 💡 الخطوة 4: تنظيف الموارد
# ----------------------------------------------------------------------------------

cap.release()
cv2.destroyAllWindows()
print("🛑 تم إغلاق الكشف بنجاح.")