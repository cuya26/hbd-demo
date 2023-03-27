import { boot } from 'quasar/wrappers'
import axios from 'axios'

// to work in local use instead this ip
const api = axios.create({ baseURL: 'http://localhost:5003' })

export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api

})

export { axios, api}
