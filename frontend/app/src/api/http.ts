import axios from 'axios';

const http = axios.create({
  baseURL: import.meta.env.VITE_REST_URL ?? '/api',
  withCredentials: true
});

export default http;

