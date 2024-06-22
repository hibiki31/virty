import Axios from 'axios'

export default Axios.create({
  baseURL: import.meta.env.VITE_APP_API_HOST,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
  responseType: 'json',
})
