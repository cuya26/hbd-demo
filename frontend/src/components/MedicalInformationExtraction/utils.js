import * as axios from "boot/axios";

export let config = {
  advanced: false,
  servers: [
    {
      name: "polimi-llama-server",
      url: axios.llamaHost,
      OpenAI_API: true,
    },
    // {
    //   name: "fornasiere-llama-server",
    //   url: axios.llamaHostAlt,
    //   OpenAI_API: true,
    // },
    // {
    //   name: "Mixtral",
    //   url: "http://147.189.192.41:8080",
    //   OpenAI_API: false,
    // },
    // {
    //   name: "Mistral8kContext",
    //   url: "http://147.189.192.78:8080",
    //   OpenAI_API: false,
    // },
  ],

  selectedServer: {
    name: "llama-server",
    url: axios.llamaHost,
    OpenAI_API: true,
  },
  customServer: {
    name: "",
    url: "",
    OpenAI_API: false,
  },
};

export function sanitizeTemplate(template) {
  return {
    assistantMessageStart: template.assistantMessageStart ?? "",
    assistantMessageEnd: template.assistantMessageEnd ?? "",
    userMessageStart: template.userMessageStart ?? "",
    userMessageEnd: template.userMessageEnd ?? "",
    systemMessageStart: template.systemMessageStart ?? "",
    systemMessageEnd: template.systemMessageEnd ?? "",
  };
}

export function applyTemplate(
  template,
  systemMessage,
  userMessage,
  completionInit,
  prevMessage
) {
  template = sanitizeTemplate(template);
  let prompt = "";
  if (prevMessage) {
    prompt += prevMessage + "\n";
    if (!prevMessage.endsWith(template.assistantMessageEnd))
      prompt += template.assistantMessageEnd;
  } else if (systemMessage !== "")
    prompt +=
      template.systemMessageStart +
      systemMessage +
      template.systemMessageEnd +
      "\n";
  prompt +=
    template.userMessageStart + userMessage + template.userMessageEnd + "\n";
  prompt += template.assistantMessageStart + completionInit;
  return prompt;
}

export function isAdvanced() {
  return config.advanced;
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
  res.replace("<dummy32000>", "");
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

//
// export function checkCustomServerAvailability() {
//   if (config.customServer.url === "") return;
//   console.log(
//     config.customServer.url + (config.customServer.OpenAI_API ? "/docs" : "")
//   );
//   axios.api
//     .get(
//       config.customServer.url + (config.customServer.OpenAI_API ? "/docs" : "")
//     )
//     .then(() => (config.customServer.reachable = true))
//     .catch((err) => {
//       console.log(err, err.code, err.code === "ERR_NETWORK");
//       config.customServer.reachable = err.code !== "ERR_NETWORK";
//     });
// }
//
// export function checkServersAvailability() {
//   for (let server of config.servers) {
//     axios.api
//       .get(server.url + (server.OpenAI_API ? "/docs" : ""))
//       .then(() => (server.reachable = true))
//       .catch((err) => {
//         console.log(err, err.code, err.code === "ERR_NETWORK");
//         server.reachable = err.code !== "ERR_NETWORK";
//       });
//   }
// }
