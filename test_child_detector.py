import cv2
import numpy as np
from ultralytics import YOLO
import os

MODEL_PATH = "models/Child_Detection_Model.pt"

def test_model_info():
    """Test 1: Check model information"""
    print("=" * 60)
    print("اختبار 1: معلومات الموديل")
    print("=" * 60)
    
    if not os.path.exists(MODEL_PATH):
        print(f"❌ الموديل غير موجود: {MODEL_PATH}")
        return False
    
    print(f"✓ الموديل موجود: {MODEL_PATH}")
    
    try:
        model = YOLO(MODEL_PATH)
        print(f"✓ تم تحميل الموديل بنجاح")
        print(f"✓ الفئات المتاحة: {model.names}")
        print(f"✓ عدد الفئات: {len(model.names)}")
        
        if 0 in model.names:
            print(f"✓ Class 0: {model.names[0]}")
        if 1 in model.names:
            print(f"✓ Class 1: {model.names[1]}")
            
        return True
    except Exception as e:
        print(f"❌ خطأ في تحميل الموديل: {e}")
        return False

def test_detection_on_image(image_path, conf_threshold=0.25):
    """Test 2: Test detection on a single image"""
    print("\n" + "=" * 60)
    print(f"اختبار 2: الكشف على صورة واحدة")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"❌ الصورة غير موجودة: {image_path}")
        print("💡 ضع صورة اختبار واستخدم: python test_child_detector.py path/to/image.jpg")
        return False
    
    print(f"✓ جاري تحليل الصورة: {image_path}")
    
    try:
        model = YOLO(MODEL_PATH)
        frame = cv2.imread(image_path)
        
        if frame is None:
            print(f"❌ فشل قراءة الصورة")
            return False
            
        h, w = frame.shape[:2]
        print(f"✓ أبعاد الصورة: {w}x{h}")
        
        # Run detection with different thresholds
        for conf in [0.15, 0.25, 0.35, 0.50]:
            print(f"\n--- اختبار بعتبة ثقة: {conf} ---")
            results = model.predict(source=frame, conf=conf, verbose=False)
            
            total_detections = 0
            child_detections = 0
            adult_detections = 0
            
            for r in results:
                if hasattr(r, "boxes") and r.boxes is not None:
                    for b in r.boxes:
                        conf_score = float(b.conf[0].item())
                        cls_id = int(b.cls[0].item())
                        xyxy = b.xyxy[0].tolist()
                        class_name = model.names.get(cls_id, f"class_{cls_id}")
                        
                        total_detections += 1
                        
                        if cls_id == 0:
                            child_detections += 1
                            print(f"  ✓ طفل: ثقة={conf_score:.3f}, مربع={[int(x) for x in xyxy]}")
                        elif cls_id == 1:
                            adult_detections += 1
                            print(f"  • بالغ: ثقة={conf_score:.3f}, مربع={[int(x) for x in xyxy]}")
            
            print(f"  إجمالي: {total_detections} كشف ({child_detections} طفل، {adult_detections} بالغ)")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الكشف: {e}")
        return False

def test_detection_from_emulator(num_frames=5):
    """Test 3: Test detection from Android emulator"""
    print("\n" + "=" * 60)
    print(f"اختبار 3: الكشف من السيميوليتر")
    print("=" * 60)
    
    SDK_ADB = "/Users/rayidalshammari/Library/Android/sdk/platform-tools/adb"
    
    if not os.path.exists(SDK_ADB):
        print(f"❌ ADB غير موجود: {SDK_ADB}")
        return False
    
    print(f"✓ ADB موجود")
    
    try:
        import subprocess
        model = YOLO(MODEL_PATH)
        
        print(f"جاري التقاط {num_frames} إطار من السيميوليتر...")
        
        for i in range(num_frames):
            print(f"\n--- إطار {i+1}/{num_frames} ---")
            
            # Capture frame
            process = subprocess.Popen(
                [SDK_ADB, "exec-out", "screencap", "-p"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            frame_bytes = process.stdout.read()
            process.wait()
            
            if not frame_bytes:
                print("❌ فشل التقاط الإطار")
                continue
            
            img_array = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if frame is None:
                print("❌ فشل فك تشفير الإطار")
                continue
            
            h, w = frame.shape[:2]
            print(f"✓ أبعاد الإطار: {w}x{h}")
            
            # Run detection
            results = model.predict(source=frame, conf=0.25, verbose=False)
            
            child_count = 0
            adult_count = 0
            
            for r in results:
                if hasattr(r, "boxes") and r.boxes is not None:
                    for b in r.boxes:
                        conf_score = float(b.conf[0].item())
                        cls_id = int(b.cls[0].item())
                        
                        if cls_id == 0:
                            child_count += 1
                            print(f"  ✓ طفل: ثقة={conf_score:.3f}")
                        elif cls_id == 1:
                            adult_count += 1
            
            print(f"  النتيجة: {child_count} طفل، {adult_count} بالغ")
            
            import time
            time.sleep(1)
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def test_clip_analysis():
    """Test 4: Test full clip analysis with tracker"""
    print("\n" + "=" * 60)
    print(f"اختبار 4: تحليل كليب كامل")
    print("=" * 60)
    
    try:
        from child_detector import analyze_clip_for_child
        import subprocess
        
        SDK_ADB = "/Users/rayidalshammari/Library/Android/sdk/platform-tools/adb"
        
        print("جاري التقاط 15 إطار من السيميوليتر...")
        
        frames = []
        for i in range(15):
            process = subprocess.Popen(
                [SDK_ADB, "exec-out", "screencap", "-p"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            frame_bytes = process.stdout.read()
            process.wait()
            
            if frame_bytes:
                img_array = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if frame is not None:
                    frames.append(frame)
            
            import time
            time.sleep(0.3)
        
        print(f"✓ تم التقاط {len(frames)} إطار")
        
        if frames:
            print("\nجاري تحليل الكليب...")
            result = analyze_clip_for_child(frames, conf=0.25)
            
            print(f"\n{'='*60}")
            print(f"النتيجة النهائية:")
            print(f"{'='*60}")
            print(f"القرار: {result['final_decision']}")
            print(f"النقاط: {result['score']:.2f}")
            print(f"معرف المسار: {result['top_id']}")
            print(f"المربع: {result['top_bbox']}")
            print(f"عدد المسارات: {len(result['metrics_by_id'])}")
            
            return True
        else:
            print("❌ لم يتم التقاط أي إطارات")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "🔍" * 30)
    print("اختبار كاشف الأطفال - Child Detector Test")
    print("🔍" * 30 + "\n")
    
    # Test 1: Model info
    if not test_model_info():
        print("\n❌ فشل اختبار معلومات الموديل. توقف.")
        return
    
    # Test 2: Detection on image (if provided)
    import sys
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        test_detection_on_image(image_path)
    else:
        print("\n💡 لاختبار صورة محددة، استخدم: python test_child_detector.py path/to/image.jpg")
    
    # Ask user if they want to test from emulator
    print("\n" + "=" * 60)
    response = input("هل تريد اختبار الكشف من السيميوليتر؟ (y/n): ")
    
    if response.lower() in ['y', 'yes', 'نعم']:
        # Test 3: Emulator detection
        test_detection_from_emulator(num_frames=5)
        
        # Test 4: Full clip analysis
        print("\n" + "=" * 60)
        response2 = input("هل تريد اختبار تحليل كليب كامل؟ (y/n): ")
        if response2.lower() in ['y', 'yes', 'نعم']:
            test_clip_analysis()
    
    print("\n" + "✅" * 30)
    print("انتهى الاختبار")
    print("✅" * 30 + "\n")

if __name__ == "__main__":
    main()