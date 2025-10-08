"""
Whisper Audio Processing Pipeline with GPT-4o-mini Classification
WHISPER1: Extract Audio
WHISPER2: Transcribe to Text
WHISPER3: GPT-4o-mini Classification
"""

import subprocess
import os
import json
from openai import OpenAI

# ============================================================
# ⚙️ CONFIGURATION - Change here only!
# ============================================================


API_KEY = os.getenv('ن')

# 2️⃣ Video file path
VIDEO_PATH = "/Users/anody/Downloads/manarah_data/v14044g50000d2u5l2fog65qra6os9k0.mp4"

# 3️⃣ Temporary audio output path
AUDIO_OUTPUT = "/tmp/extracted_audio.wav"

# 4️⃣ GPT model for classification
GPT_MODEL = "gpt-4o-mini"  # Fast and cheap!

# ============================================================


def extract_audio(video_path, audio_output):
    """Extract audio from video file using FFmpeg"""
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return False
    
    print("⚙️  Extracting audio...")
    
    cmd = [
        'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
        '-ar', '16000', '-ac', '1', '-y', audio_output
    ]
    
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return os.path.exists(audio_output)
    except:
        print("❌ FFmpeg error. Install: brew install ffmpeg")
        return False


def transcribe_audio(audio_path, api_key):
    """Transcribe audio to text using Whisper API"""
    
    print("⚙️  Transcribing audio...")
    
    try:
        client = OpenAI(api_key=api_key)
        
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ar",
                response_format="verbose_json",
                prompt="This is an audio recording in Gulf Arabic dialect"
            )
        
        return response
        
    except Exception as e:
        print(f"❌ Whisper API error: {e}")
        return None


def classify_with_gpt(transcript, api_key, model=GPT_MODEL):
    """Classify transcript using GPT-4o-mini with Saudi-specific prompt"""
    
    print("⚙️  Classifying content...")
    
    # Saudi-specific classification system prompt
    system_prompt = """# نظام تحليل المحتوى الصوتي - اللهجة السعودية
# Saudi Arabic Audio Content Moderation System

## دورك ومهمتك | Your Role

أنت نموذج ذكاء اصطناعي متخصص في تحليل النصوص العربية المحولة من كلام شفهي (من Whisper). مهمتك تحليل هذه النصوص وكشف المخالفات بدقة عالية مع فهم السياق الثقافي السعودي وطبيعة الكلام الشفهي.

---

## ملاحظات مهمة عن النصوص القادمة من Whisper

⚠️ **خصائص النصوص الصوتية:**
- قد تحتوي على أخطاء إملائية أو نسخ غير دقيق
- قد تفتقد علامات الترقيم
- قد تحتوي على كلمات غير واضحة أو مقطوعة
- قد تكون باللهجة العامية المحكية بشكل كامل
- **ركز على المعنى العام وليس الدقة اللغوية**

---

## الفئات المعتمدة | Approved Categories

### 1. **bullying** - تنمّر
**الوصف:** أي محتوى يهدف للإساءة، السخرية، أو الاستهزاء بشخص أو مجموعة

**أمثلة شفهية:**
- "يا قزم / يا فاشل / يا غبي"
- "يا عوري / يا طفلة / يا حيوان"
- "ايش الهرجة / شكلك / انت مين"
- "شكلك كذا / وجهك مره قبيح"
- "انت ما تسوى شي / ما عندك قيمة"
- "يا حقير / يا تافه / يا ضعيف"
- السخرية من المظهر أو القدرات

**مستوى الثقة:** 0.85+ للحالات الواضحة

---

### 2. **inappropriate_words** - شتائم عامة
**الوصف:** استخدام ألفاظ نابية، شتائم، أو كلمات مسيئة عامة (غير جنسية)

**أمثلة:**
- "يا نذل / يا وقح / يا خبيث"
- "يا كلب / يا حمار / يا خنزير"
- "يعن ابوك / الله يلعنك"
- شتم الذات الإلهية (حاشا لله)
- سب الوالدين أو الأهل
- "يا ابن ال..."

**ملاحظة:** الشتائم العامة فقط، أما الشتائم الجنسية فتدخل في الفئة التالية

**مستوى الثقة:** 0.90+ للشتائم الصريحة

---

### 3. **brag_about_money** - تباهي بالمال
**الوصف:** التفاخر بالمال، الثروة، أو الممتلكات بطريقة استعراضية

**أمثلة شفهية:**
- "أنا أغنى واحد هنا / عندي فلوس ما تتخيلها"
- "سيارتي أغلى من بيتك"
- "أنا عندي مليون / مليونين"
- "كل يوم أصرف ألف ريال"
- "فلوسي كثيرة مره / ما يهمني المبلغ"
- "أنا أقدر أشتري اللي أبيه"

**لا يعتبر تباهياً:**
- ذكر السعر في سياق طبيعي
- الحديث عن راتب أو دخل بدون استعراض
- مشاركة إنجاز مالي بتواضع

**مستوى الثقة:** 0.75-0.90 حسب الوضوح

---

### 4. **racism** - عنصرية
**الوصف:** التمييز ضد مجموعة بناءً على العرق، الجنسية، الأصل، القبيلة، أو اللون

**أمثلة شفهية:**
- "امشي يا أسود" (بنبرة إهانة)
- "يا عبد / يا زنجي"
- "العمال الهنود / البنقاليين دول كذا"
- "الشعب الفلاني كلهم..."
- "القبيلة دي ما تسوى"
- "السود / البيض كلهم نفس الشي"
- "اللهجة الفلانية مضحكة / قبيحة"
- تعميمات سلبية عن جنسيات

**حساسية خاصة:**
- العنصرية قد تكون خفية
- انتبه للتعميمات السلبية
- راعِ السياق

**مستوى الثقة:** 0.75-0.95

---

### 5. **using_child_as_content** - استغلال الأطفال كمحتوى
**الوصف:** استخدام الأطفال كمحتوى لفظياً، مثل: "هذا ولدي يلعب" أو تكليفهم بعمل محتوى

**أمثلة شفهية:**
- "هذا ولدي / بنتي يلعب / تلعب"
- "شوفوا الطفل / البيبي يسوي كذا"
- "عندي بنت صغيرة تسوي ترند"
- "خليت ولدي يصور معي"
- "الأطفال حقي يسوون فيديوهات"
- "بنتي الصغيرة تغني / ترقص"

**معايير صارمة:**
- أي إشارة لاستخدام طفل في المحتوى = مخالفة
- حماية الطفل أولوية قصوى
- الثقة العالية مطلوبة: 0.90+

---

### 6. **inappropriate_sexual_words** - كلمات جنسية غير لائقة
**الوصف:** استخدام ألفاظ جنسية فاحشة، إيحاءات جنسية صريحة، أو كلمات مبتذلة ذات طابع جنسي

**أمثلة:**
- أسماء أعضاء جنسية بطريقة فاحشة
- أفعال جنسية بطريقة صريحة
- شتائم ذات طابع جنسي
- وصف أفعال جنسية بشكل فاحش
- تلميحات جنسية صريحة ومبتذلة

**ملاحظة:** هذه فئة منفصلة عن الشتائم العامة، مخصصة للمحتوى الجنسي فقط

**مستوى الثقة:** 0.90+ للحالات الصريحة

---

### 7. **neutral** - محايد
**الوصف:** نص طبيعي لا يحتوي على أي مخالفة

**أمثلة:**
- "اليوم الجو جميل"
- "كيف حالك؟ وين رايح؟"
- "أنا رايح السوق"
- "شكراً والله / يعطيك العافية"
- "شايفين لمعة العقال ونقشته" (حديث عن ملابس)
- محادثات يومية عادية

---

## منهجية التحليل | Analysis Methodology

### خطوات التحليل المتسلسلة:

1. **قراءة النص** 
   - اقرأ النص الصوتي كاملاً
   - تجاهل الأخطاء الإملائية البسيطة

2. **فهم السياق**
   - ما الموقف؟ من المتكلم؟
   - هل هذا كلام عفوي أم مقصود؟

3. **البحث عن مخالفات**
   - ابدأ بالفئات الأخطر: استغلال الأطفال، الشتائم الجنسية
   - ثم الشتائم العامة والتنمر
   - ثم العنصرية والتباهي

4. **تحديد الفئة الأنسب**
   - اختر فئة واحدة فقط
   - إذا كان هناك أكثر من مخالفة، اختر الأخطر

5. **قياس مستوى الثقة**
   - ما مدى وضوح المخالفة؟
   - هل هناك احتمال لتفسير آخر؟

6. **كتابة السبب بوضوح**
   - اشرح لماذا صنفت النص هكذا
   - كن مختصراً وواضحاً

---

## تنسيق الإخراج | Output Format

**⚠️ مهم جداً: أخرج JSON فقط بدون أي نص قبله أو بعده**

### في حالة المخالفة:
```json
{
  "category": "اسم_الفئة_بالإنجليزية",
  "violation": true,
  "confidence": 0.00,
  "reason": "شرح مختصر وواضح بالعربية"
}
```

### في حالة المحتوى المحايد:
```json
{
  "category": "neutral",
  "violation": false,
  "confidence": 0.99,
  "reason": "النص طبيعي ولا يحتوي على مخالفة"
}
```

---

## ترتيب الأولويات | Priority Order

عند وجود أكثر من مخالفة محتملة، اختر حسب الأولوية:

1. **using_child_as_content** - الأطفال أولاً
2. **inappropriate_sexual_words** - محتوى جنسي فاحش
3. **inappropriate_words** - شتائم عامة
4. **bullying** - تنمر
5. **racism** - عنصرية
6. **brag_about_money** - تباهي

---

## معايير الثقة | Confidence Levels

- **0.95 - 1.00**: واضح تماماً، لا شك فيه
- **0.85 - 0.94**: واضح جداً مع احتمال ضئيل للخطأ
- **0.70 - 0.84**: مرجح بقوة لكن يحتمل تفسيراً آخر
- **0.50 - 0.69**: غير واضح تماماً، لكن هذا أرجح
- **أقل من 0.50**: اختر "neutral" في حالة الشك الكبير

---

**الآن جاهز لتحليل النصوص. أرسل النص وسأحلله فوراً.**"""
    
    user_message = f"""حلل هذا النص الصوتي:

"{transcript}"

أخرج JSON فقط."""

    try:
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"❌ GPT error: {e}")
        return {
            "category": "neutral",
            "violation": False,
            "confidence": 0.5,
            "reason": "حدث خطأ في التحليل"
        }


def display_results(transcript, classification):
    """Display final results - clean and minimal"""
    
    category = classification.get("category", "unknown")
    is_violation = classification.get("violation", False)
    confidence = classification.get("confidence", 0.0)
    reason = classification.get("reason", "لا يوجد سبب")
    
    print("\n" + "="*70)
    print("📊 RESULTS | النتائج")
    print("="*70)
    
    # Transcript
    print(f"\n📝 Text | النص:\n{transcript}")
    
    # Classification
    status = "⚠️ VIOLATION | مخالفة" if is_violation else "✅ SAFE | آمن"
    print(f"\n{status}")
    print(f"Category: {category}")
    print(f"Confidence: {confidence:.0%}")
    print(f"Reason: {reason}")
    
    # Action (only if violation)
    if is_violation:
        if confidence >= 0.90:
            print(f"Action: 🔴 REMOVE | إزالة")
        elif confidence >= 0.75:
            print(f"Action: 🟠 REVIEW | مراجعة")
        else:
            print(f"Action: 🟡 WARNING | تحذير")
    
    print("="*70)
    
    # Save to file
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write(f"Text: {transcript}\n")
        f.write(f"Category: {category}\n")
        f.write(f"Violation: {is_violation}\n")
        f.write(f"Confidence: {confidence:.0%}\n")
        f.write(f"Reason: {reason}\n")


def cleanup(audio_path):
    """Delete temporary audio file"""
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except:
        pass


def main():
    """Main pipeline: Extract → Transcribe → Classify"""
    
    print("\n🎙️ Audio Content Moderation")
    print(f"📁 Video: {VIDEO_PATH}\n")
    
    # Step 1: Extract audio
    if not extract_audio(VIDEO_PATH, AUDIO_OUTPUT):
        print("❌ Failed at audio extraction")
        return
    
    # Step 2: Transcribe
    response = transcribe_audio(AUDIO_OUTPUT, API_KEY)
    if not response:
        print("❌ Failed at transcription")
        cleanup(AUDIO_OUTPUT)
        return
    
    # Step 3: Classify
    classification = classify_with_gpt(response.text, API_KEY)
    
    # Display results
    display_results(response.text, classification)
    
    # Cleanup
    cleanup(AUDIO_OUTPUT)
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()