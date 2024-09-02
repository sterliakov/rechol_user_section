import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:80',
  withCredentials: true,
});
// FIXME: this should depend on the selected locale
axiosInstance.defaults.headers.common['Accept-Language'] = 'ru';
export default axiosInstance;
