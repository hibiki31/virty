import axios from '@/axios/index'
import { setCookie, removeCookie } from 'typescript-cookie'

export async function setAxios(accessToken: string) {
  setCookie('accessToken', accessToken)
  await axios.interceptors.request.use(
    (config) => {
      config.headers.Authorization = 'Bearer ' + accessToken
      return config
    },
    (err) => {
      return Promise.reject(err)
    },
  )
}

export async function removeAuth() {
  await setAxios('')
  removeCookie('accessToken')
}
