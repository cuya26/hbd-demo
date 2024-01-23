import { boot } from "quasar/wrappers";
import axios from "axios";

// to work in local use instead this ip
// const api = axios.create({ baseURL: 'http://localhost:51119' })
// const patientSearchApi = axios.create({ baseURL: 'http://localhost:51125' })

const featurePropertiesHost = "http://localhost:8082";
const llamaAltCompletions = "http://147.189.193.77";
const llamaHost = "http://131.175.15.22:61111/llama-server";
const api = axios.create({
  baseURL: "http://131.175.15.22:61111/hbd-demo-api/",
});
const patientSearchApi = axios.create({
  baseURL: "http://131.175.15.22:61111/patient-search-server/",
});
export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios;
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api;
  app.config.globalProperties.$api = patientSearchApi;
});

export {
  axios,
  api,
  patientSearchApi,
  llamaHost,
  llamaAltCompletions,
  featurePropertiesHost,
};
