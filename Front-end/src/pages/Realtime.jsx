import React, { useEffect, useRef, useState } from 'react'
import NotificationCard from '../components/NotificationCard.jsx'

// Helper to play a beep on new notifications
function useBeep(){
  const ctxRef = useRef(null);
  return () => {
    const ctx = ctxRef.current || new (window.AudioContext || window.webkitAudioContext)();
    ctxRef.current = ctx;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = 'sine'; o.frequency.value = 880;
    o.connect(g); g.connect(ctx.destination);
    g.gain.setValueAtTime(0.001, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.05, ctx.currentTime + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.25);
    o.start(); o.stop(ctx.currentTime + 0.3);
  }
}

// 👇 القوائم خارج Realtime component أو داخل useEffect فوق fallback
const IMAGE_KINDS = [
  "استغلال الأطفال كمحتوى",
  "التباهي بالأموال أو الممتلكات",
  "إثارة القبلية أو العنصرية أو الطائفية",
  "كشف الجسد من الكتفين حتى الساقين"
];
const AUDIO_KINDS = [
  "التنمر أو الاستهزاء بالآخرين",
  "الألفاظ المبتذلة"
];

export default function Realtime(){
  const [imageEvents, setImageEvents] = useState([]);
  const [audioEvents, setAudioEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const beep = useBeep();

  useEffect(() => {
    const src = new EventSource('/api/events');
    src.onopen = () => setConnected(true);
    src.onerror = () => setConnected(false);
    src.onmessage = (e) => {
      try{
        const ev = JSON.parse(e.data);
        addEvent(ev);
        beep();
      } catch(err){ console.error(err); }
    }

    // ✅ fallback when SSE not available
    const fallback = setInterval(() => {
      if (connected) return;
      const now = Date.now();
      const isImage = Math.random() > 0.5;

      const sample = {
        id: now,
        ts: now,
        kind_ar: isImage 
          ? IMAGE_KINDS[1]
          : AUDIO_KINDS[0],
        status: Math.random() > 0.6 ? 'verified' : 'pending',
        type: isImage ? 'image' : 'audio',
        image_url: isImage ? '/assets/wrong.jpg' : undefined,
        audio_url: !isImage ? '/assets/sample-voice.mp3' : undefined,
        title: isImage ? 'لقطة شاشة' : 'مقطع صوتي',
        desc: isImage 
          ? 'تم اكتشاف احتمالي لمخالفة ضمن الصور'
          : 'تم اكتشاف احتمالي لمخالفة صوتية'
      };

      addEvent(sample);
      beep();
    }, 4000);

    function addEvent(ev){
      if(ev.type === 'image'){ 
        setImageEvents(prev => [ev, ...prev].slice(0, 50)); 
      } else { 
        setAudioEvents(prev => [ev, ...prev].slice(0, 50)); 
      }
    }

    return () => { src.close(); clearInterval(fallback); }
  }, [connected]);

  return (
    <section className="realtime">
      <div className="page-title sadu-heading">
        الكشف في الوقت الفعلي
        <span className={`dot ${connected ? 'on' : 'off'}`}></span>
      </div>
      <div className="columns">
        <div className="col left">
          <h3>إشعارات صوتية</h3>
          {audioEvents.length === 0 && <p className="empty">لا توجد إشعارات حتى الآن</p>}
          {audioEvents.map(ev => <NotificationCard key={ev.id} item={ev} />)}
        </div>
        <div className="col right">
          <h3>إشعارات بصريّة (صور)</h3>
          {imageEvents.length === 0 && <p className="empty">لا توجد إشعارات حتى الآن</p>}
          {imageEvents.map(ev => <NotificationCard key={ev.id} item={ev} />)}
        </div>
      </div>
    </section>
  )
}
