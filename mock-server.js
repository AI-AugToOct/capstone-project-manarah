// Simple SSE mock server (run: npm run mock)
import http from 'http';

const clients = new Set();

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

// Push a random event every 5s
setInterval(() => {
  const isImage = Math.random() > 0.5;
  const ev = {
    id: Date.now(),
    ts: Date.now(),
    type: isImage ? 'image' : 'audio',
    kind_ar: isImage ? 'ملابس غير لائقة' : 'تنمّر لفظي',
    status: Math.random() > 0.6 ? 'verified' : 'pending',
    image_url: isImage ? 'https://picsum.photos/seed/' + Math.floor(Math.random()*1000) + '/320/180' : undefined,
    audio_url: !isImage ? 'https://www2.cs.uic.edu/~i101/SoundFiles/StarWars60.wav' : undefined,
    title: isImage ? 'لقطة شاشة' : 'مقطع صوتي',
    desc: isImage ? 'اكتشاف احتمالي لمخالفة مظهر' : 'محتوى لفظي قد يحتوي تنمّر'
  };
  const data = `data: ${JSON.stringify(ev)}\n\n`;
  for (const res of clients) res.write(data);
}, 5000);
