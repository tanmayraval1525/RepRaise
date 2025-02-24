import axios from 'axios';

// Create an Axios instance for API calls
const api = axios.create({
  baseURL: 'http://localhost:5000', // URL of your Flask backend
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
