import React, {useEffect, useState} from 'react'

export default function Inbox(){
  const [reviews, setReviews] = useState<any[]>([])
  useEffect(()=>{
    fetch('http://localhost:8000/reviews', { headers: {'x-api-key':'supersecret'}})
      .then(r=>r.json()).then(setReviews).catch(()=>setReviews([]))
  },[])
  return (
    <div>
      <h2>Inbox</h2>
      <ul>
        {reviews.map(r=> <li key={r.id}>{r.location} — {r.text}</li>)}
      </ul>
    </div>
  )
}
