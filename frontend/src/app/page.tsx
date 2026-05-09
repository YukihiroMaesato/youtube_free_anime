'use client';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

import { useEffect, useState } from 'react';

export default function Home() {
  const [result, setResult] = useState<string>('loading...');

  useEffect(() => {
    fetch(`${API_URL}/api/health`)
      .then(res => res.json())
      .then(data => {
        setResult(JSON.stringify(data, null, 2));
      })
      .catch(err => {
        setResult('error: ' + err.message);
      });
  }, []);

  return (
    <main>
      {API_URL}
      <h1>Laravel Health Check eeeee</h1>
      <pre>{result}</pre>
    </main>
  );
}