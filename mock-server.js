// mock-server.js
import http from 'http';

const clients = new Set();

// التصنيفات المحتملة
const IMAGE_KINDS = [
  "استغلال الأطفال كمحتوى",
  "الألفاظ المبتذلة أو التباهي بالأموال أو الممتلكات",
  "إثارة القبلية أو العنصرية أو الطائفية",
  "كشف الجسد من الكتفين حتى الساقين"
];

const AUDIO_KINDS = [
  "التنمر أو الاستهزاء بالآخرين"
];

http.createServer((req, res) => {
  if (req.url === '/api/events') {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
      'Access-Control-Allow-Origin': '*',
    });
    res.write('\n');
    clients.add(res);
    req.on('close', () => clients.delete(res));
  } else {
    res.writeHead(200);
    res.end('OK');
  }
}).listen(7070, () => console.log('SSE mock on http://localhost:7070'));

setInterval(() => {
  const isImage = Math.random() > 0.5;

  const ev = {
    id: Date.now(),
    ts: Date.now(),
    type: isImage ? 'image' : 'audio',
    kind_ar: isImage 
      ? IMAGE_KINDS[Math.floor(Math.random() * IMAGE_KINDS.length)]
      : AUDIO_KINDS[0],
    status: Math.random() > 0.6 ? 'verified' : 'pending',
    image_url: isImage ? 'https://picsum.photos/seed/' + Math.floor(Math.random()*1000) + '/320/180' : undefined,
    audio_url: !isImage ? 'https://www2.cs.uic.edu/~i101/SoundFiles/StarWars60.wav' : undefined,
    title: isImage ? 'لقطة شاشة' : 'مقطع صوتي',
    desc: isImage 
      ? 'تم اكتشاف احتمالي لمخالفة ضمن الصور'
      : 'تم اكتشاف احتمالي لمخالفة صوتية'
  };

  const data = `data: ${JSON.stringify(ev)}\n\n`;
  for (const res of clients) res.write(data);
}, 5000);
