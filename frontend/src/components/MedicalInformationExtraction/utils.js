import * as axios from "boot/axios";
import { api, llamaServer, baseApi } from "boot/axios";

export let config = {
  advanced: true,
  servers: [
    {
      name: "polimi-llama-server",
      url: llamaServer,
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
    {
      name: "Llama3",
      url: "http://147.189.192.78:8080",
      OpenAI_API: false,
    },
  ],

  selectedServer: {
    name: "polimi-llama-server",
    url: llamaServer,
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
    assistantMessageStart: template?.assistantMessageStart ?? "",
    assistantMessageEnd: template?.assistantMessageEnd ?? "",
    userMessageStart: template?.userMessageStart ?? "",
    userMessageEnd: template?.userMessageEnd ?? "",
    systemMessageStart: template?.systemMessageStart ?? "",
    systemMessageEnd: template?.systemMessageEnd ?? "",
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
  return axios.baseApi
    .post(
      buildLLMUrl(),
      {
        ...body,
        stream: false,
        cache_prompt: true,
        stop: ["<|im_end|>", "###", '<|eot_id|>'],
      },
      {
        "Content-Type": "application/json",
        timeout: 600000,
      }
    )
    .then(mapLLMAnswer);
}

export function sendMessageToLLM(chat, params) {
  return fetch(llamaServer + "/v1/chat/completions", {
    method: "POST",
    body: JSON.stringify({
      messages: chat,
      stream: true,
      cache_prompt: true,
      ...params,
    }),
    headers: {
      "Content-Type": "application/json",
      timeout: 36000,
    },
  }).then((response) => {
    if (!response.ok) {
      throw new Error("Errore nella chiamata POST");
    }
    return response.body;
  });
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
