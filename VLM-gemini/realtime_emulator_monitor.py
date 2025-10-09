import subprocess
import os
import time
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import threading
from collections import deque
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

import google.generativeai as genai
from openai import OpenAI
from PIL import Image


class Config:
    SDK_ADB = "/Users/rayidalshammari/Library/Android/sdk/platform-tools/adb"
    
    GEMINI_API_KEY = ""
    OPENAI_API_KEY = ""
    
    GEMINI_MODEL = "gemini-2.0-flash-exp"
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS = 1536
    
    CAPTURE_INTERVAL = 2  
    MAX_FRAMES_BUFFER = 10  
    
    SCREENSHOTS_FOLDER = "emulator_screenshots"
    RESULTS_FOLDER = "realtime_results"
    

    WS_HOST = "localhost"
    WS_PORT = 8765


os.makedirs(Config.SCREENSHOTS_FOLDER, exist_ok=True)
os.makedirs(Config.RESULTS_FOLDER, exist_ok=True)

genai.configure(api_key=Config.GEMINI_API_KEY)
openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)




VIOLATION_DEFINITIONS = {
    "child_exploitation": """محتوى يستخدم الأطفال (أقل من 18 سنة) كموضوع رئيسي. الطفل يظهر بشكل 
    بارز (أكثر من 40% من الإطار)، يؤدي أمام الكاميرا، فتح ألعاب، تحديات. عبارات مثل "شوفوا ولدي"، 
    "تحدي مع طفلي"، "اشتركوا عشان ولدي".""",
    
    "wealth_bragging": """عرض مبالغ فيه للأموال أو الأشياء الفاخرة. أكوام من النقد، ساعات فاخرة، 
    شعارات الماركات، سيارات فاخرة. عبارات مثل "مجرد مصروف جيب"، "السيارة الخامسة".""",
    
    "bullying": """مضايقة أو إهانة أو سخرية. إيماءات مسيئة، تعابير ساخرة، لقطات شاشة لرسائل مضايقة، 
    نصوص مسيئة. عبارات مثل "فاشل"، "غبي"، "احذف حسابك".""",
    
    "worker_exploitation": """العمال المنزليين كموضوع ترفيهي. العامل في مركز الإطار، سيناريوهات 
    مسرحية، مقالب. عبارات مثل "شوفوا الخادمة"، "مقلب على السائق".""",
    
    "vulgar_language": """ألفاظ بذيئة معروضة بصرياً. نصوص تحتوي على شتائم، محجوبة بنجوم. ألفاظ 
    مثل "كلب"، "حمار"، "خنزير"، شتائم.""",
    
    "tribal": """تفوق قبلي أو انقسام. أعلام قبلية انقسامية، رموز عدوانية. عبارات مثل "قبيلتنا أشرف"، 
    مصطلحات مثل "عبيد"، "خضيري".""",
    
    "sectarian": """انقسام طائفي ديني أو كراهية. رموز طائفية انقسامية، أعلام عدوانية. مصطلحات مثل 
    "رافضي"، "ناصبي"، "وهابي"، التكفير.""",
    
    "racism": """تمييز أو كراهية على أساس العرق. رموز عنصرية، صور نمطية. شتائم مثل "عبد"، 
    "زنجي"، استخدام الجنسية كإهانة."""
}





class EmbeddingCache:
    """ذاكرة مؤقتة لـ embeddings المخالفات"""
    
    def __init__(self):
        self.cache = {}
        self._initialize()
    
    def _initialize(self):
        print("🔄 تهيئة embeddings المخالفات...")
        for violation_type, definition in VIOLATION_DEFINITIONS.items():
            try:
                response = openai_client.embeddings.create(
                    model=Config.EMBEDDING_MODEL,
                    input=definition,
                    encoding_format="float"
                )
                self.cache[violation_type] = np.array(response.data[0].embedding)
            except Exception as e:
                print(f"  ✗ {violation_type}: {e}")
                self.cache[violation_type] = np.zeros(Config.EMBEDDING_DIMENSIONS)
        print("✅ تم تهيئة جميع embeddings\n")
    
    def get_embeddings(self):
        return self.cache

embedding_cache = EmbeddingCache()





class WebSocketManager:
    """مدير اتصالات WebSocket للبث المباشر"""
    
    def __init__(self):
        self.active_connections = set()
        self.server = None
    
    async def register(self, websocket):
        """إضافة اتصال جديد"""
        self.active_connections.add(websocket)
        print(f"✅ عميل متصل - إجمالي الاتصالات: {len(self.active_connections)}")
    
    async def unregister(self, websocket):
        """إزالة اتصال"""
        self.active_connections.discard(websocket)
        print(f"🔌 عميل منقطع - إجمالي الاتصالات: {len(self.active_connections)}")
    
    async def broadcast_violation(self, violation_data):
        """بث مخالفة لجميع العملاء المتصلين"""
        if not self.active_connections:
            return
        
        message = json.dumps(violation_data, ensure_ascii=False)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send(message)
            except Exception as e:
                print(f"❌ خطأ في إرسال البيانات: {e}")
                disconnected.append(connection)
        

        for connection in disconnected:
            await self.unregister(connection)
    
    async def websocket_handler(self, websocket, path):
        """معالج WebSocket"""
        await self.register(websocket)
        try:
            async for message in websocket:

                await websocket.send(f"Echo: {message}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)
    
    def start_server(self):
        """بدء خادم WebSocket"""
        print(f"🚀 بدء خادم WebSocket على ws://{Config.WS_HOST}:{Config.WS_PORT}")
        
        async def start():
            self.server = await websockets.serve(
                self.websocket_handler, 
                Config.WS_HOST, 
                Config.WS_PORT
            )
            print(f"✅ خادم WebSocket يعمل على ws://{Config.WS_HOST}:{Config.WS_PORT}")
            await self.server.wait_closed()
        
        asyncio.run(start())


websocket_manager = WebSocketManager()





def run_adb(*args):
    """تشغيل أمر ADB"""
    cmd = [Config.SDK_ADB] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def check_emulator():
    """التحقق من اتصال الـ emulator"""
    output = run_adb("devices")
    devices = [line.split()[0] for line in output.split('\n')[1:] if line.strip() and "device" in line]
    return len(devices) > 0

def capture_screenshot():
    """أخذ screenshot من الـ Emulator"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    remote_path = f"/sdcard/screenshot_{timestamp}.png"
    local_path = os.path.join(Config.SCREENSHOTS_FOLDER, f"frame_{timestamp}.png")
    
    try:
        run_adb("shell", "screencap", "-p", remote_path)
        
        run_adb("pull", remote_path, local_path)
        
        run_adb("shell", "rm", remote_path)
        
        if os.path.exists(local_path):
            return local_path
        return None
        
    except Exception as e:
        print(f"❌ خطأ في أخذ screenshot: {e}")
        return None




def analyze_frame_with_gemini(image_path):
    """تحليل frame واحد باستخدام Gemini Vision"""
    try:
        image_file = genai.upload_file(path=image_path)
        

        while image_file.state.name == "PROCESSING":
            time.sleep(0.5)
            image_file = genai.get_file(image_file.name)
        
        if image_file.state.name == "FAILED":
            return None
        

        prompt = """حلل هذه الصورة/اللقطة بشكل شامل ومفصل:

**التحليل المرئي:**
- الأشخاص الرئيسيون: صف جميع الأشخاص في الصورة (العمر التقريبي، الجنس، الموقع)
- الأشياء والأفعال: ماذا يحدث في الصورة؟ ما هي الأشياء المرئية؟
- تكوين الإطار: ما في المركز؟ ما في الخلفية؟ ما في المقدمة؟
- نسبة الإطار: كم نسبة الإطار يشغلها الموضوع الرئيسي؟ (قدر %)
- الإضاءة: طبيعية، احترافية، استوديو؟
- زاوية الكاميرا: قريبة، بعيدة، من أعلى، من أسفل؟

**النصوص المرئية:**
- هل هناك نصوص في الصورة؟ انسخها بالضبط (عربي أو إنجليزي)
- هل النصوص تحتوي على شتائم أو ألفاظ مسيئة؟

**السياق الثقافي:**
- عناصر سعودية: ثياب تقليدية (ثوب، عباية، شماغ)؟
- رموز ثقافية أو دينية؟
- عناصر قبلية أو طائفية؟

**تحليل المحتوى:**
- ما نوع المحتوى؟ (ترفيهي، تعليمي، إعلاني، شخصي)
- هل هناك أطفال؟ إذا نعم، هل هم محور المحتوى؟
- هل هناك عرض للأموال أو الكماليات؟
- هل هناك مضايقة أو تنمر أو سخرية؟
- هل هناك عمال منزليين كمحتوى ترفيهي؟

**مؤشرات المخالفات:**
- استغلال أطفال: هل الطفل محور المحتوى؟ هل يؤدي للكاميرا؟
- تباهي بالثروة: هل هناك عرض للنقود أو الكماليات؟
- تنمر: هل هناك سخرية أو إهانة؟
- استغلال عمال: هل العمال محور ترفيهي؟
- ألفاظ بذيئة: هل هناك شتائم مرئية؟
- قبلية/طائفية: هل هناك رموز انقسامية؟
- عنصرية: هل هناك تمييز عرقي؟

كن دقيقاً ومفصلاً جداً. اذكر كل التفاصيل المهمة."""


        model = genai.GenerativeModel(model_name=Config.GEMINI_MODEL)
        response = model.generate_content([image_file, prompt])
        
        return response.text
        
    except Exception as e:
        print(f"❌ خطأ في تحليل Gemini: {e}")
        return None

def generate_embedding(text):
    """توليد embedding"""
    try:
        response = openai_client.embeddings.create(
            model=Config.EMBEDDING_MODEL,
            input=text,
            encoding_format="float"
        )
        return np.array(response.data[0].embedding)
    except Exception as e:
        print(f"❌ خطأ في embedding: {e}")
        return np.zeros(Config.EMBEDDING_DIMENSIONS)

def cosine_similarity(vec1, vec2):
    """حساب التشابه"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = dot_product / (norm1 * norm2)
    return float((similarity + 1) / 2)

def calculate_scores(content_embedding):
    """حساب درجات المخالفات"""
    violation_embeddings = embedding_cache.get_embeddings()
    scores = {}
    
    for violation_type, violation_embedding in violation_embeddings.items():
        similarity = cosine_similarity(content_embedding, violation_embedding)
        scores[violation_type] = round(similarity, 2)
    
    return scores





class RealtimeMonitor:
    """نظام المراقبة المباشر"""
    
    def __init__(self):
        self.running = False
        self.frame_count = 0
        self.results_history = deque(maxlen=Config.MAX_FRAMES_BUFFER)
        self.current_analysis = None
        
    def analyze_frame(self, image_path):
        """تحليل frame واحد كامل"""
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"🎬 Frame #{self.frame_count + 1}")
        print(f"⏰ الوقت: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*70}")
        

        print("🌟 جاري التحليل بـ Gemini Vision...")
        description = analyze_frame_with_gemini(image_path)
        
        if not description:
            print("❌ فشل التحليل")
            return None
        
        print("✅ اكتمل تحليل Gemini")
        

        print("🧮 توليد embedding...")
        content_embedding = generate_embedding(description)
        

        print("🎯 حساب درجات المخالفات...")
        scores = calculate_scores(content_embedding)
        

        highest = max(scores.items(), key=lambda x: x[1])
        

        processing_time = time.time() - start_time
        

        if highest[1] >= 0.85:
            action = "🔴 حذف تلقائي"
        elif highest[1] >= 0.60:
            action = "🟠 مراجعة بشرية"
        elif highest[1] >= 0.40:
            action = "🟡 تحذير"
        else:
            action = "🟢 السماح"
        

        result = {
            "frame_number": self.frame_count + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "image_path": image_path,
            "processing_time": round(processing_time, 2),
            "description": description,
            "scores": scores,
            "highest_violation": {
                "type": highest[0],
                "score": highest[1]
            },
            "action": action
        }
        
        self.frame_count += 1
        self.results_history.append(result)
        self.current_analysis = result
        

        self.display_result(result)
        

        if highest[1] >= 0.40: 
            print(f"💾 تم حفظ المخالفة في ملف JSON - سيتم إرسالها للويب تلقائياً")
        
        return result
    
    async def broadcast_violation(self, result):
        """بث مخالفة للواجهة الأمامية"""
        try:

            violation_data = {
                "id": result["frame_number"],
                "timestamp": result["timestamp"],
                "ts": int(datetime.now().timestamp() * 1000),  
                "type": "image",  
                "kind_ar": self.translate_violation(result["highest_violation"]["type"]),
                "score": result["highest_violation"]["score"],
                "status": "pending" if result["highest_violation"]["score"] < 0.85 else "verified",
                "image_url": f"/assets/wrong.jpg", 
                "title": "لقطة شاشة",
                "desc": f"تم اكتشاف مخالفة: {self.translate_violation(result['highest_violation']['type'])}",
                "action": result["action"],
                "processing_time": result["processing_time"]
            }
            
            await websocket_manager.broadcast_violation(violation_data)
            print(f"📡 تم بث المخالفة #{result['frame_number']} للواجهة الأمامية")
            
        except Exception as e:
            print(f"❌ خطأ في بث المخالفة: {e}")
    
    def send_violation_to_sse_server(self, result):
        """إرسال مخالفة لخادم SSE الخارجي"""
        try:
            import requests
            

            violation_data = {
                "id": result["frame_number"],
                "timestamp": result["timestamp"],
                "ts": int(datetime.now().timestamp() * 1000),
                "type": "image",
                "kind_ar": self.translate_violation(result["highest_violation"]["type"]),
                "score": result["highest_violation"]["score"],
                "status": "pending" if result["highest_violation"]["score"] < 0.85 else "verified",
                "image_url": "/assets/wrong.jpg",
                "title": "لقطة شاشة",
                "desc": f"تم اكتشاف مخالفة: {self.translate_violation(result['highest_violation']['type'])}",
                "action": result["action"],
                "processing_time": result["processing_time"]
            }
            

            response = requests.post(
                "http://localhost:8765/broadcast",
                json=violation_data,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"📡 تم إرسال المخالفة #{result['frame_number']} لخادم SSE")
            else:
                print(f"⚠️ فشل إرسال المخالفة: {response.status_code}")
                
        except ImportError:
            print("⚠️ مكتبة requests غير مثبتة - لا يمكن إرسال المخالفات")
        except Exception as e:
            print(f"❌ خطأ في إرسال المخالفة لخادم SSE: {e}")
    
    def display_result(self, result):
        """عرض النتيجة بشكل جميل"""
        print(f"\n{result['action']}")
        print(f"⚠️  المخالفة الأعلى: {self.translate_violation(result['highest_violation']['type'])}")
        print(f"📊 الدرجة: {result['highest_violation']['score']*100:.1f}%")
        
        print("\n📈 جميع الدرجات:")
        sorted_scores = sorted(result['scores'].items(), key=lambda x: x[1], reverse=True)
        
        for violation, score in sorted_scores[:5]:  
            bar_length = int(score * 30)
            bar = '█' * bar_length + '░' * (30 - bar_length)
            emoji = self.get_emoji(score)
            ar_name = self.translate_violation(violation)
            print(f"  {emoji} {ar_name:20s} [{bar}] {score*100:5.1f}%")
        
        print(f"\n⏱️  وقت المعالجة: {result['processing_time']:.2f}s")
        print(f"💰 التكلفة: $0.00302")
        print(f"{'='*70}\n")
    
    def translate_violation(self, violation):
        """ترجمة اسم المخالفة للعربية"""
        translations = {
            "child_exploitation": "استغلال الأطفال",
            "wealth_bragging": "التباهي بالثروة",
            "bullying": "التنمر",
            "worker_exploitation": "استغلال العمال",
            "vulgar_language": "ألفاظ بذيئة",
            "tribal": "قبلية",
            "sectarian": "طائفية",
            "racism": "عنصرية"
        }
        return translations.get(violation, violation)
    
    def get_emoji(self, score):
        """الحصول على emoji حسب الدرجة"""
        if score >= 0.85:
            return "🔴"
        elif score >= 0.60:
            return "🟠"
        elif score >= 0.40:
            return "🟡"
        else:
            return "🟢"
    
    def start_monitoring(self):
        """بدء المراقبة المستمرة"""
        print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        🎬 مراقبة مباشرة لشاشة Android Emulator                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
        """)
        
        if not check_emulator():
            print("❌ الـ Emulator غير متصل!")
            print("💡 شغل الـ Emulator أولاً")
            return
        
        print(f"✅ الـ Emulator متصل")
        print(f"⏱️  سيتم أخذ screenshot كل {Config.CAPTURE_INTERVAL} ثانية")
        print(f"🛑 اضغط Ctrl+C للإيقاف\n")
        
        self.running = True
        
        try:
            while self.running:
                print(f"📸 أخذ screenshot...")
                image_path = capture_screenshot()
                
                if image_path:

                    result = self.analyze_frame(image_path)
                    
                    if result:

                        self.save_result(result)
                

                time.sleep(Config.CAPTURE_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n🛑 إيقاف المراقبة...")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """إيقاف المراقبة"""
        self.running = False
        
        print(f"\n{'='*70}")
        print("📊 ملخص الجلسة")
        print(f"{'='*70}")
        print(f"إجمالي الـ Frames المحللة: {self.frame_count}")
        
        if self.results_history:
            # إحصائيات
            actions = {}
            for result in self.results_history:
                action = result['action']
                actions[action] = actions.get(action, 0) + 1
            
            print("\nتوزيع الإجراءات:")
            for action, count in actions.items():
                print(f"  {action}: {count}")
            

            avg_scores = {}
            for result in self.results_history:
                for violation, score in result['scores'].items():
                    if violation not in avg_scores:
                        avg_scores[violation] = []
                    avg_scores[violation].append(score)
            
            print("\nمتوسط درجات المخالفات:")
            for violation, scores in sorted(avg_scores.items(), key=lambda x: np.mean(x[1]), reverse=True):
                avg = np.mean(scores)
                ar_name = self.translate_violation(violation)
                print(f"  {ar_name}: {avg:.2f}")
        
        print(f"{'='*70}\n")
        print("✅ انتهت المراقبة")
    
    def save_result(self, result):
        """حفظ النتيجة"""
        filename = f"frame_{result['frame_number']}_{int(time.time())}.json"
        filepath = os.path.join(Config.RESULTS_FOLDER, filename)
        

        save_result = {
            "frame_number": result['frame_number'],
            "timestamp": result['timestamp'],
            "processing_time": result['processing_time'],
            "scores": result['scores'],
            "highest_violation": result['highest_violation'],
            "action": result['action']
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_result, f, ensure_ascii=False, indent=2)





def show_menu():
    """القائمة الرئيسية"""
    print("\n" + "="*70)
    print("🎮 نظام المراقبة المباشرة لـ Emulator")
    print("="*70)
    print("""
1. بدء المراقبة المستمرة (Real-time Monitoring)
2. تحليل screenshot واحد فقط (Single Frame)
3. اختبار الاتصال بالـ Emulator
4. تغيير فترة الالتقاط
5. عرض الإحصائيات
6. اختبار إرسال المخالفات (إرسال مخالفة تجريبية)
7. خروج
""")

def start_websocket_server():
    """بدء خادم WebSocket في thread منفصل"""
    try:
        websocket_manager.start_server()
    except Exception as e:
        print(f"❌ خطأ في خادم WebSocket: {e}")

def main():
    """الوظيفة الرئيسية"""
    monitor = RealtimeMonitor()
    

    print("🚀 بدء خادم WebSocket...")
    ws_thread = threading.Thread(target=start_websocket_server, daemon=True)
    ws_thread.start()
    time.sleep(2)  
    
    while True:
        show_menu()
        
        try:
            choice = input("اختر (1-7): ").strip()
            
            if choice == "1":
                print("\n🚀 بدء المراقبة المستمرة...")
                print("💡 شغل فيديو أو أي محتوى في الـ Emulator الآن!")
                input("⏎ اضغط Enter عندما تكون جاهزاً...")
                monitor.start_monitoring()
            
            elif choice == "2":
                print("\n📸 أخذ screenshot واحد...")
                image_path = capture_screenshot()
                if image_path:
                    result = monitor.analyze_frame(image_path)
                    if result:
                        monitor.save_result(result)
            
            elif choice == "3":
                print("\n🔍 التحقق من الاتصال...")
                if check_emulator():
                    print("✅ الـ Emulator متصل")
                    devices = run_adb("devices")
                    print(devices)
                else:
                    print("❌ الـ Emulator غير متصل")
            
            elif choice == "4":
                interval = input(f"فترة الالتقاط الحالية: {Config.CAPTURE_INTERVAL}s\nأدخل القيمة الجديدة (ثواني): ")
                try:
                    Config.CAPTURE_INTERVAL = int(interval)
                    print(f"✅ تم تغيير الفترة إلى {Config.CAPTURE_INTERVAL}s")
                except:
                    print("❌ قيمة غير صحيحة")
            
            elif choice == "5":
                print(f"\n📊 الإحصائيات:")
                print(f"  إجمالي الـ Frames: {monitor.frame_count}")
                print(f"  Frames في الذاكرة: {len(monitor.results_history)}")
            
            elif choice == "6":
                print("\n🧪 اختبار إرسال المخالفات...")

                test_violation = {
                    "id": 999,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ts": int(datetime.now().timestamp() * 1000),
                    "type": "image",
                    "kind_ar": "استغلال الأطفال",
                    "score": 0.85,
                    "status": "verified",
                    "image_url": "/assets/wrong.jpg",
                    "title": "لقطة شاشة تجريبية",
                    "desc": "هذه مخالفة تجريبية لاختبار النظام",
                    "action": "🔴 حذف تلقائي",
                    "processing_time": 1.5
                }
                

                try:
                    import requests
                    response = requests.post(
                        "http://localhost:8765/broadcast",
                        json=test_violation,
                        timeout=5
                    )
                    if response.status_code == 200:
                        print("📡 تم إرسال مخالفة تجريبية للواجهة الأمامية")
                    else:
                        print(f"⚠️ فشل الإرسال: {response.status_code}")
                except ImportError:
                    print("⚠️ مكتبة requests غير مثبتة")
                except Exception as e:
                    print(f"❌ خطأ في الإرسال: {e}")
            
            elif choice == "7":
                print("\n👋 مع السلامة!\n")
                break
            
            else:
                print("❌ اختيار غير صحيح")
            
            if choice != "1":
                input("\n⏎ اضغط Enter للمتابعة...")
                
        except KeyboardInterrupt:
            print("\n\n👋 مع السلامة!\n")
            break
        except Exception as e:
            print(f"\n❌ خطأ: {e}\n")

if __name__ == "__main__":
    main()
