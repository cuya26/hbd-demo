import * as axios from "boot/axios";

export let config = {
  servers: [
    {
      name: "llama-server",
      url: axios.llamaHost,
      OpenAI_API: true,
      reachable: false,
    },
    {
      name: "fornasiere-llama-server",
      url: axios.llamaHostAlt,
      OpenAI_API: true,
      reachable: false,
    },
    {
      name: "Mixtral",
      url: "http://147.189.192.41:8080",
      OpenAI_API: false,
      reachable: false,
    },
  ],

  selectedServer: {
    name: "llama-server",
    url: axios.llamaHost,
    OpenAI_API: true,
    reachable: false,
  },
  customServer: {
    name: "",
    url: "",
    OpenAI_API: false,
    reachable: false,
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
  console.log((
    config.selectedServer.url +
    (config.selectedServer.OpenAI_API ? "/v1/completions" : "/completion")
  ))
  return (
    config.selectedServer.url +
    (config.selectedServer.OpenAI_API ? "/v1/completions" : "/completion")
  );
}

function mapLLMAnswer(response) {
  let res = "";
  if (config.selectedServer.OpenAI_API) {
    res = response.data.choices[0].text;
  } else {
    res = response.data.content;
  }
  return res;
}

export function saveServer() {
  config.servers.push(config.customServer);
  config.customServer = {
    name: "",
    url: "",
    OpenAI_API: false,
    reachable: false,
  };
}

export function checkCustomServerAvailability() {
  if (config.customServer.url === "") return;
  console.log(
    config.customServer.url + (config.customServer.OpenAI_API ? "/docs" : "")
  );
  axios.api
    .get(
      config.customServer.url + (config.customServer.OpenAI_API ? "/docs" : "")
    )
    .then(() => (config.customServer.reachable = true))
    .catch((err) => {
      console.log(err, err.code, err.code === "ERR_NETWORK");
      config.customServer.reachable = err.code !== "ERR_NETWORK";
    });
}

export function checkServersAvailability() {
  for (let server of config.servers) {
    axios.api
      .get(server.url + (server.OpenAI_API ? "/docs" : ""))
      .then(() => (server.reachable = true))
      .catch((err) => {
        console.log(err, err.code, err.code === "ERR_NETWORK");
        server.reachable = err.code !== "ERR_NETWORK";
      });
  }
}
