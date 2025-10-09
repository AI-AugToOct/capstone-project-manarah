import React from 'react'

export default function NotificationCard({ item }){
  return (
    <div className={`card ${item.type === 'audio' ? 'audio' : 'image'}`}>
      <div className="card-header">
        <span className="badge kind">
          {item.kind_ar}
        </span>
        <span className={`badge status ${item.status === 'verified' ? 'ok' : 'pending'}`}>
          {item.status === 'verified' ? 'تم التحقق' : 'قيد المراجعة'}
        </span>
        <span className="timestamp">{new Date(item.ts).toLocaleTimeString('ar-SA')}</span>
      </div>
      <div className="card-body">
        {item.type === 'image' ? (
          <img src={item.image_url} alt="screenshot" className="screenshot" />
        ) : (
          <audio controls src={item.audio_url} />
        )}
        <div className="meta">
          <p className="title">{item.title}</p>
          <p className="desc">{item.desc}</p>
        </div>
      </div>
    </div>
  )
}
