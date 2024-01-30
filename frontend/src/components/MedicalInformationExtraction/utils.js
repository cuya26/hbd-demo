import * as axios from "boot/axios";

export let config = {
  OpenAI_API: true,

  servers: [
    { name: "llama-server", url: axios.llamaHost },
    {
      name: "fornasiere-llama-server",
      url: axios.llamaHostAlt,
    },
    {
      name: "Mixtral",
      url: "http://147.189.192.41:8080",
    },
  ],
  selectedServer: { name: "llama-server", url: axios.llamaHost },
  customServer: {
    name: "",
    url: "",
  },
};

export function getTemplate() {
  return axios.api.get("/get_template");
}
export function applyTemplate(
  template,
  userMessage,
  systemMessage,
  completionInit
) {
  return template
    .replace("{system_message}", systemMessage)
    .replace("{prompt}", userMessage)
    .replace("{completion_init}", completionInit);
}
export function setProperties(task, properties) {
  return axios.api.post("/set_properties/" + task, properties);
}

export function getProperties(task) {
  return axios.api.get("/get_properties/" + task);
}

export async function getTasks() {
  return axios.api.get("/get_tasks");
}

export function askLLM(body) {
  return axios.api
    .post(
      buildLLMUrl(),
      {
        ...body,
        stream: false,
        stop: ["<|im_end|>", "###"],
      },
      {
        "Content-Type": "application/json",
        timeout: 600000,
      }
    )
    .then(mapLLMAnswer);
}

export function buildLLMUrl() {
  return (
    config.selectedServer.url +
    (config.OpenAI_API ? "/v1/completions" : "/completion")
  );
}

function mapLLMAnswer(response) {
  let res = "";
  if (config.OpenAI_API) {
    res = response.data.choices[0].text;
  } else {
    res = response.data.content;
  }
  return res;
}

export function checkServersAvailability() {
  for (let server of this.servers) {
    axios.api
      .get(server.url + "/docs")
      .then(() => (server.reachable = true))
      .catch(() => (server.reachable = false));
  }
}
