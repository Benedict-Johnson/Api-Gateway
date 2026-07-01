import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 50 }, // Ramp up to 50 users
    { duration: '20s', target: 50 }, // Stay at 50 users
    { duration: '10s', target: 0 },  // Ramp down
  ],
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const HEADERS = {
  'X-API-Key': __ENV.API_KEY_SECRET || 'secret123',
};

export default function () {
  // Test fast endpoint (cached)
  let res = http.get(`${BASE_URL}/users`, { headers: HEADERS });
  check(res, {
    'users status is 200': (r) => r.status === 200,
  });

  // Test slow endpoint to trigger circuit breaker/retries eventually
  let slowRes = http.get(`${BASE_URL}/slow`, { headers: HEADERS });
  check(slowRes, {
    'slow status is 504 or 503': (r) => r.status === 504 || r.status === 503,
  });

  sleep(1);
}
