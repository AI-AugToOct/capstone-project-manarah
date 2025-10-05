"""
نظام تحليل المحتوى باستخدام Whisper + GPT-4 Vision
Real-Time Video Moderation System with OpenAI APIs
"""

import json
import base64
import cv2
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from openai import OpenAI
import os


@dataclass
class ModerationResult:
    """نتيجة التحليل المنظمة"""
    violation_detected: bool
    violation_type: List[str]
    confidence: float  # 0-100
    evidence: List[str]
    action: str  # "notify_backend" or "log_only"
    timestamp: str
    frame_id: Optional[str] = None
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


class ViolationCategories:
    """تصنيفات المخالفات"""
    
    VISUAL = {
        'children_content': 'استغلال الأطفال كمحتوى',
        'money_display': 'التباهي بالأموال أو الممتلكات',
        'violence_weapons': 'العنف أو الأسلحة',
        'nudity_inappropriate': 'كشف الجسد من الكتفين حتى الساقين',
        'flags_symbols': 'الرموز السياسية أو الدينية'
    }
    
    TEXTUAL = {
        'bullying': 'التنمر أو الاستهزاء بالآخرين',
        'family_privacy': 'كشف خصوصيات الأسرة وخلافاتها',
        'profanity_wealth': 'الألفاظ المبتذلة أو التباهي بالأموال',
        'tribal_racism': 'إثارة القبلية أو العنصرية أو الطائفية'
    }


class VideoModerationAgent:
    """وكيل تحليل الفيديو الذكي"""
    
    def __init__(self, api_key: str, frames_per_second: int = 2):
        """
        Args:
            api_key: مفتاح OpenAI API
            frames_per_second: عدد الإطارات المراد تحليلها في الثانية
        """
        self.client = OpenAI(api_key=api_key)
        self.fps_analysis = frames_per_second
        self.confidence_threshold = 70.0
        
    def extract_audio_from_video(self, video_path: str, output_audio: str = "temp_audio.mp3") -> str:
        """
        استخراج الصوت من الفيديو
        """
        try:
            # استخدام ffmpeg لاستخراج الصوت
            import subprocess
            command = [
                'ffmpeg', '-i', video_path,
                '-vn',  # بدون فيديو
                '-acodec', 'libmp3lame',
                '-y',  # الكتابة فوق الملف إذا كان موجوداً
                output_audio
            ]
            subprocess.run(command, check=True, capture_output=True)
            return output_audio
        except Exception as e:
            print(f"⚠️ تحذير: فشل استخراج الصوت - {e}")
            return None
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """
        تحويل الصوت إلى نص باستخدام Whisper
        """
        print("🎤 جاري تحليل الصوت...")
        
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ar",
                    response_format="verbose_json"  # للحصول على timestamps
                )
            
            return {
                "text": transcription.text,
                "language": "ar",
                "duration": getattr(transcription, 'duration', 0)
            }
        except Exception as e:
            print(f"❌ خطأ في تحليل الصوت: {e}")
            return {"text": "", "language": "ar", "duration": 0}
    
    def extract_frames(self, video_path: str) -> List[Dict]:
        """
        استخراج إطارات من الفيديو
        """
        print(f"🎬 جاري استخراج الإطارات ({self.fps_analysis} إطار/ثانية)...")
        
        cap = cv2.VideoCapture(video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # حساب كم إطار نريد تخطيه
        frame_interval = int(video_fps / self.fps_analysis) if video_fps > 0 else 1
        
        frames = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                # تحويل الإطار إلى base64
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                timestamp = frame_count / video_fps if video_fps > 0 else 0
                
                frames.append({
                    "frame_id": f"frame_{len(frames)}",
                    "timestamp": round(timestamp, 2),
                    "base64": frame_base64
                })
            
            frame_count += 1
        
        cap.release()
        print(f"✅ تم استخراج {len(frames)} إطار من أصل {total_frames}")
        return frames
    
    def analyze_frame_with_gpt4v(self, frame_base64: str, frame_id: str) -> Dict:
        """
        تحليل إطار واحد باستخدام GPT-4 Vision
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # أو "gpt-4-vision-preview"
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """قم بتحليل هذه الصورة واكتشف المخالفات التالية:
1. ظهور أطفال كمحتوى
2. عرض الأموال أو الممتلكات الفاخرة
3. العنف أو الأسلحة
4. كشف الجسد من الكتفين حتى الساقين
5. أعلام سياسية أو رموز دينية
6. أي نص مكتوب في الصورة (OCR)

أرجع JSON فقط بهذا الشكل:
{
    "violations": ["نوع المخالفة"],
    "descriptions": ["وصف تفصيلي"],
    "confidence_scores": [0-100],
    "ocr_text": "النص المكتوب"
}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{frame_base64}",
                                    "detail": "low"  # استخدم "high" لدقة أعلى
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            # استخراج النتيجة
            content = response.choices[0].message.content
            
            # محاولة تحليل JSON
            try:
                result = json.loads(content)
            except:
                # إذا لم يكن JSON صحيح، نحاول استخراجه
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {"violations": [], "descriptions": [], "confidence_scores": [], "ocr_text": ""}
            
            return {
                "frame_id": frame_id,
                "violations": result.get("violations", []),
                "descriptions": result.get("descriptions", []),
                "confidence": result.get("confidence_scores", []),
                "ocr_text": result.get("ocr_text", "")
            }
            
        except Exception as e:
            print(f"❌ خطأ في تحليل الإطار {frame_id}: {e}")
            return {
                "frame_id": frame_id,
                "violations": [],
                "descriptions": [],
                "confidence": [],
                "ocr_text": ""
            }
    
    def moderate_text_with_gpt4(self, transcript: str, visual_context: List[Dict]) -> Dict:
        """
        تحليل النص المنطوق باستخدام GPT-4
        """
        print("🤖 جاري تحليل النص المنطوق...")
        
        visual_summary = "\n".join([
            f"- الإطار {v['frame_id']}: {', '.join(v['violations']) if v['violations'] else 'لا يوجد مخالفات'}"
            for v in visual_context[:5]  # أول 5 إطارات فقط
        ])
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "أنت نظام فحص محتوى متخصص في اكتشاف المخالفات في المحتوى العربي."
                    },
                    {
                        "role": "user",
                        "content": f"""قم بتحليل هذا المحتوى واكتشف المخالفات:

النص المنطوق:
{transcript}

السياق البصري:
{visual_summary}

المخالفات المطلوب اكتشافها:
1. التنمر أو الاستهزاء بالآخرين
2. كشف خصوصيات الأسرة وخلافاتها
3. استغلال الأطفال كمحتوى
4. الألفاظ المبتذلة أو التباهي بالأموال أو الممتلكات
5. إثارة القبلية أو العنصرية أو الطائفية
6. كشف الجسد من الكتفين حتى الساقين

"_comment": "هذا الملف يحتوي على قائمة كلمات وعبارات حساسة للرقابة على المحتوى في السعودية، موزعة على 6 فئات: التنمر، الشتائم العامة، التباهي بالمال، العنصرية بكل أشكالها، استغلال الأطفال في المحتوى، والكلمات الجنسية غير اللائقة. الكلمات مدمجة من جميع المناطق واللهجات المحلية.",

  "brag_about_money": [
    "أنا أغنى واحد", "قصري كبير", "سيارتي فيراري", "عندي ملايين", "رصيدي بالبنك مليان",
    "أصرف بدون حساب", "ساعتي رولكس", "طقم ذهب", "طيارتي الخاصة", "شركاتي كثيرة",
    "فلوسي ما تخلص", "أشتري اللي أبغى", "براندات عالمية", "أفخم سيارة", "شقة في لندن",
    "فلوس ورث", "أعيش رفاهية", "قصورنا كثيرة", "أرضي واسعة", "أغلى لبس", 
    "سكني في برج", "فلوس كاش", "عندي خدم وسواقين", "أشتري الناس", "أجمع سيارات"
  ],

  "inappropriate_sexual_words": [
    "قحبة", "شرموطة", "متناك", "لوطي", "شاذ", "سالب", "موجب", "زب", "كس", "طيز",
    "مني", "ممارسة", "خنيث", "بزران جنس" , "أنيكك", "أحط فيك", "نكحتك", "مصاصة",
    "عاهرة", "جنس", "مقاطع فاضحة", "إباحية", "يلعب بذاته", "علاقات محرمة","يا عري", "قذر جنسياً"
  ],

  "racism": [
    "يا عبد", "يا خوال", "يا طرشي", "يا طرطور", "يا قروي", "يا بدوي", "يا حضري",
    "يا خضيري", "يا عجم", "مو أصيل", "مو من قبيلتنا", "ما نزوج منكم", "دمكم وسخ",
    "كلكم جهلة", "أنت من الطبقة الواطية", "أنت مو أصيل", "يا جاهل", "يا خونة",
    "يا سودة", "يا متخلف", "عيال العبيد", "مو من جماعتنا", "يا عنصري", "يا عديمي الأصل",
    "يا مجوسي", "يا روافض", "يا نواصب", "يا سني", "يا شيعي"
  ],

  "using_child_as_content": [
    "أستغل طفلي محتوى", "أعلن بولدي", "أصور بنتي بتيك توك", "أخلي بنتي ترقص", "أستعرض بنتي بالإنستغرام",
    "أصور طفلي في اللايف", "أصور أولادي مقالب", "أعلن بطفل", "أصور طفلي باليوتيوب", "أستغل الطفولة",
    "أفضح طفلي بالسوشال", "أصور بنتي بملابس ضيقة", "أستعرض ولدي مشهور", "أستخدم الأطفال إعلان",
    "أخلي بنتي تقلد مشاهير", "أستغل الطفل عشان ترند", "أصور ولدي ترند", "أخلي طفلي يمثل",
    "أعلن بأطفالي", "أصور بنتي بدون إذن", "أستغل بنتي مشاهدات", "أكسب مشاهدات من ولدي",
    "أستخدم الأطفال دعاية", "أصور بنتي للمتابعين", "أخلي ولدي يقلد مشاهير"
  ],

  "bullying": [
    "يا غبي", "يا أهبل", "يا دبة", "يا قزم", "يا وجه قبيح", "يا معفن", "يا مسخرة",
    "يا فاشل", "ما عندك عقل", "تافه", "شكلك يضحك", "يا معاق", "أنت ولا شي", "أنت ثقيل دم",
    "يا كلب", "يا تيس", "أنت تنمر", "ما حد يحبك", "يا ضفدع", "يا طرطور", "وجهك وسخ",
    "محد يطيقك", "أنت عالة", "يا حيوان", "أنت مقرف"
  ],

  "inappropriate_words": [
    "يا حيوان", "يا كلب", "يا تافه", "يا وسخ", "يا قذر", "يا غثيث", "يا حقير", "يا نذل",
    "يلعن شكلك", "يلعن أمك", "يلعن أبوك", "يلعن خيرك", "يلعن أصلك", "تف عليك",
    "يا مقرف", "يا خنزير", "يا زبالة", "يا قملة", "يا بلا مخ", "يا مسعور",
    "ما تسوى", "انقلع", "اختفي", "يا متخلف", "يا بليد"
  ]
   
أرجع JSON فقط:
{{
    "violations": ["نوع المخالفة"],
    "evidence": ["دليل نصي من المحتوى"],
    "confidence": [0-100],
    "severity": "low/medium/high"
}}"""
                    }
                ],
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            
            # تحليل JSON
            try:
                result = json.loads(content)
            except:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {"violations": [], "evidence": [], "confidence": [], "severity": "low"}
            
            return result
            
        except Exception as e:
            print(f"❌ خطأ في تحليل النص: {e}")
            return {"violations": [], "evidence": [], "confidence": [], "severity": "low"}
    
    def analyze_video(self, video_path: str) -> ModerationResult:
        """
        تحليل فيديو كامل
        """
        print("=" * 60)
        print("🚀 بدء تحليل الفيديو")
        print("=" * 60)
        
        # 1. استخراج الصوت وتحليله
        audio_path = self.extract_audio_from_video(video_path)
        transcript_result = {"text": ""}
        
        if audio_path and os.path.exists(audio_path):
            transcript_result = self.transcribe_audio(audio_path)
            
            # حفظ النص المستخرج
            with open("transcript_output.txt", "w", encoding="utf-8") as f:
                f.write(transcript_result["text"])
            print(f"💾 تم حفظ النص في: transcript_output.txt")
            
            # حذف الملف المؤقت
            try:
                os.remove(audio_path)
            except:
                pass
        
        # 2. استخراج وتحليل الإطارات
        frames = self.extract_frames(video_path)
        
        visual_violations = []
        for i, frame_data in enumerate(frames[:10]):  # تحليل أول 10 إطارات فقط (للتوفير)
            print(f"🔍 تحليل الإطار {i+1}/{min(10, len(frames))}...")
            result = self.analyze_frame_with_gpt4v(
                frame_data["base64"],
                frame_data["frame_id"]
            )
            visual_violations.append(result)
        
        # 3. تحليل النص مع السياق البصري
        text_violations = self.moderate_text_with_gpt4(
            transcript_result["text"],
            visual_violations
        )
        
        # 4. دمج النتائج (Late Fusion)
        all_violations = []
        all_evidence = []
        confidence_scores = []
        
        # إضافة المخالفات البصرية
        for v_result in visual_violations:
            violations_list = v_result.get("violations", [])
            confidence_list = v_result.get("confidence", [])
            descriptions_list = v_result.get("descriptions", [])
            
            # التأكد من أن confidence قائمة
            if isinstance(confidence_list, (int, float)):
                confidence_list = [confidence_list] * len(violations_list)
            elif not isinstance(confidence_list, list):
                confidence_list = []
            
            for i, violation in enumerate(violations_list):
                conf = confidence_list[i] if i < len(confidence_list) else 50
                if conf >= self.confidence_threshold:
                    all_violations.append(violation)
                    desc = descriptions_list[i] if i < len(descriptions_list) else violation
                    all_evidence.append(f"إطار {v_result['frame_id']}: {desc}")
                    confidence_scores.append(conf)
        
        # إضافة المخالفات النصية
        text_confidence = text_violations.get("confidence", [])
        # التعامل مع حالة confidence كرقم أو قائمة
        if isinstance(text_confidence, (int, float)):
            text_confidence = [text_confidence] * len(text_violations.get("violations", []))
        elif not isinstance(text_confidence, list):
            text_confidence = []
        
        for i, violation in enumerate(text_violations.get("violations", [])):
            conf = text_confidence[i] if i < len(text_confidence) else 50
            if conf >= self.confidence_threshold:
                all_violations.append(violation)
                evidence_list = text_violations.get("evidence", [])
                evidence = evidence_list[i] if i < len(evidence_list) else violation
                all_evidence.append(f"نص منطوق: {evidence}")
                confidence_scores.append(conf)
        
        # 5. إنشاء النتيجة النهائية
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        max_confidence = max(confidence_scores) if confidence_scores else 0
        
        result = ModerationResult(
            violation_detected=len(all_violations) > 0,
            violation_type=list(set(all_violations)),  # إزالة التكرارات
            confidence=round(avg_confidence, 2),
            evidence=all_evidence,
            action="notify_backend" if max_confidence >= 80 else "log_only",
            timestamp=datetime.now().isoformat(),
            frame_id=None
        )
        
        # حفظ النتيجة
        with open("moderation_result.json", "w", encoding="utf-8") as f:
            f.write(result.to_json())
        
        print("\n" + "=" * 60)
        print("✅ اكتمل التحليل")
        print("=" * 60)
        
        return result


def main():
    """الدالة الرئيسية"""
    
    # 1. ضع مفتاح API هنا
    API_KEY = ""  # ضع مفتاحك هنا
    
    if not API_KEY:
        print("❌ خطأ: يرجى إضافة مفتاح OpenAI API")
        return
    
    # 2. مسار الفيديو
    VIDEO_PATH = "/Users/rayidalshammari/Desktop/git-proj/capstone-project-manarah/test1.mp4"
    
    if not os.path.exists(VIDEO_PATH):
        print(f"❌ خطأ: الملف غير موجود: {VIDEO_PATH}")
        return
    
    # 3. إنشاء الوكيل وتحليل الفيديو
    agent = VideoModerationAgent(
        api_key=API_KEY,
        frames_per_second=2  # تحليل إطارين في الثانية
    )
    
    result = agent.analyze_video(VIDEO_PATH)
    
    # 4. طباعة النتيجة
    print("\n📋 النتيجة النهائية:")
    print(result.to_json())
    
    if result.violation_detected:
        print(f"\n⚠️ تم اكتشاف {len(result.violation_type)} مخالفة")
        for violation in result.violation_type:
            print(f"   - {violation}")
    else:
        print("\n✅ لم يتم اكتشاف أي مخالفات")


if __name__ == "__main__":
    main()