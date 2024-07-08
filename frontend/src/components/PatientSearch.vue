<template>
  <div class="row justify-evenly">
    <div class="row">
      <q-card class="column no-wrap" style="width: 40%; height: 680px">
        <div class="row">
          <!-- PatientSearch -->
          <q-card-section class="row">
            <div class="col-2"></div>
            <div class="text-h6 text-primary">Patient Search</div>
            <div class="col-2"></div>
            <q-card-section class="q-pt-md" style="height: 75px">
              <div style="width: 100%" class="q-pa-sm">
                <div class="row no-wrap" style="width: 100%">
                  <q-input
                    style="width: 100%"
                    rounded
                    outlined
                    dense
                    v-model="patientSearchText"
                    placeholder="Write a condition"
                    @keyup.enter="searchPatient"
                  />
                  <div class="q-px-sm"></div>
                  <q-btn
                    :loading="loadingPatientSearch"
                    round
                    color="primary"
                    icon="search"
                    @click="searchPatient"
                  />
                </div>
              </div>
            </q-card-section>
            <div class="col-2"></div>
            <div class="text-h6 text-primary">Search Results:</div>
            <div class="col-2"></div>
            <div
              class="q-pt-md"
              style="display: flex; justify-content: space-between"
            >
              <div class="table-container">
                <table>
                  <tbody>
                    <tr v-if="combinedResults.length === 0">
                      <td class="empty-row">No results found</td>
                    </tr>
                    <tr
                      v-else
                      v-for="(row, index) in combinedResults"
                      :key="index"
                      :class="{ highlighted: selectedRow === index }"
                      @click="
                        selectRow(index);
                        attachCriteria(row);
                      "
                    >
                      <td v-html="row.context"></td>
                    </tr>
                    <tr
                      v-if="loadingPatientSearch || loadingCriteriaCheck"
                      class="loading-container"
                    >
                      <td colspan="1">
                        <q-inner-loading showing color="primary" />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!-- <div class="table-container" style="height: 490px; width: 100%;">

                <q-table
                  class="my-sticky-virtscroll-table"
                  :rows-per-page-options="[0]"
                  dense
                  separator="cell"
                  :columns="patientColumns"
                  :rows="combinedResults"
                  :loading="loadingPatientSearch || loadingCriteriaCheck"
                  style="width: 100%; height:100%;"
                >
                  <template v-slot:loading>
                    <q-inner-loading showing color="primary" />
                  </template>
                  <template v-slot:body="props">
                    <q-tr :props="props">
                      <q-td v-for="col in patientColumns" :key="col.name" :props="props">
                        <pre
                          style="white-space: nowrap; text-wrap: wrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer;"
                          v-html="props.row[col.field]"
                          @click="attachCriteria(props.row)"
                        ></pre>
                      </q-td>
                    </q-tr>
                  </template>
                </q-table>
              </div>  -->
            </div>
          </q-card-section>
        </div>
      </q-card>
      <!-- Middle Card -->
      <q-card class="column no-wrap" style="width: 60%; height: 680px">
        <div class="row">
          <!-- Inclusion/Exclusion Criteria -->
          <q-card style="width: 100%; height: 250px">
            <q-card-section class="row justify-between" style="height: 5%">
              <div class="col-2"></div>
              <div class="text-h6 text-primary">
                Inclusion/Exclusion Criteria
              </div>
              <div class="col-2"></div>
            </q-card-section>
            <q-card-section class="" style="height: 80%">
              <div style="width: 100%" class="q-pa-sm">
                <div class="q-pa-sm" style="width: 100%">
                  <q-input
                    style="width: 100%; max-height: 150px"
                    type="textarea"
                    outlined
                    dense
                    v-model="criteriacheckText"
                    placeholder="Inclusion-Exclusion Criteria"
                    @keyup.enter="criteriaCheck"
                  />
                  <div class="q-px-sm"></div>
                  <q-btn
                    :loading="loadingCriteriaCheck"
                    round
                    color="primary"
                    icon="search"
                    @click="criteriaCheck"
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>
          <!-- ChatBot Output -->
          <q-card style="width: 100%; height: 430px">
            <q-card-section class="row justify-between" style="height: 5%">
              <div class="col-2"></div>
              <div class="text-h6 text-primary">ChatBot Output</div>
              <div class="col-2"></div>
            </q-card-section>
            <q-card-section class="" style="height: 90%">
              <div
                v-if="loadingChatBot"
                class="column justify-center items-center no-wrap col-12"
                style="height: 100%"
              >
                <q-spinner color="primary" size="6em" />
              </div>
              <div
                v-if="!loadingChatBot"
                class="column justify-center items-center no-wrap col-12"
                style="height: 100%"
              >
                <div
                  class="row justify-start items-center"
                  style="width: 100%"
                ></div>
                <div
                  style="
                    height: 100%;
                    width: 100%;
                    border-radius: 4px;
                    border: 1.5px solid #bdc3c7;
                  "
                  class="overflow-auto q-pa-md"
                  ref="chatWindow"
                >
                  <div class="q-px-sm row justify-center" style="height: 100%">
                    <div class="col-12">
                      <div
                        v-for="chatLine in chatHistory"
                        :key="chatLine"
                        :class="
                          'row justify-' +
                          chatConfig['chatLinePosition'][chatLine.role] +
                          ' q-py-sm'
                        "
                      >
                        <div
                          :class="
                            'bg-' +
                            chatConfig['chatLineColor'][chatLine.role] +
                            ' q-pa-sm'
                          "
                          style="
                            border-radius: 12px;
                            width: fit-content;
                            max-width: 60%;
                            white-space: pre-line;
                          "
                        >
                          {{ chatLine.content }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="q-pa-sm"></div>
                <div class="row justify-center no-wrap" style="width: 100%">
                  <q-input
                    style="width: 100%"
                    rounded
                    outlined
                    dense
                    v-model="inputText"
                    placeholder="Write a message"
                    @keyup.enter="
                      loadingChatResponse ? true : sendMessage(inputText)
                    "
                  />
                  <div class="q-px-sm"></div>
                  <q-btn
                    icon="cleaning_services"
                    @click="loadingChatResponse ? true : resetChatHistory()"
                    rounded
                    color="warning"
                    dense
                  />
                  <div class="q-px-sm"></div>
                  <q-btn
                    icon="attach_file"
                    @click="loadingChatResponse ? true : attachDocument()"
                    rounded
                    color="secondary"
                    dense
                  />
                  <div class="q-px-sm"></div>
                  <q-btn
                    :loading="loadingChatResponse"
                    round
                    color="primary"
                    icon="send"
                    @click="sendMessage(inputText)"
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </q-card>
    </div>
  </div>
</template>

<style>
.table-container {
  position: relative;
  max-height: 490px; /* Set the desired height */
  overflow-y: auto; /* Enable vertical scrolling */
  border: 1px solid #b9b9b9; /* Border for the table container */
  border-radius: 8px; /* Rounded corners */
  padding: 8px; /* Add padding inside the container to separate the border from the table content */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Optional: add a shadow for better visual appearance */
}

table {
  width: 100%;
  border-collapse: collapse; /* Collapse borders */
  position: relative;
}

td {
  border-top: 1px solid #ddd;
  border-bottom: 1px solid #ddd;
  padding: 8px;
}

tr:first-child td {
  border-top: none; /* Remove top border for the first row */
}

tr:last-child td {
  border-bottom: none; /* Remove bottom border for the last row */
}

tr.highlighted {
  background-color: #f0f0f0; /* Light blue background for highlighted row */
}

tr:hover {
  background-color: #f5f5f5;
  cursor: pointer;
}
.empty-row {
  height: 400px; /* Match the height of the container to ensure the table size is consistent */
  text-align: center; /* Center the text */
  vertical-align: middle; /* Vertically center the text */
  color: #999; /* Lighter color for the empty state text */
}

.loading-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(
    255,
    255,
    255,
    0.8
  ); /* Semi-transparent background to overlay the table */
  border-radius: 16px; /* Match the rounded corners of the table container */
}
</style>

<!-- <style lang="sass">
.highlighted-row
  background-color: #f0f0f0 /* Choose your desired highlight color */

.my-sticky-virtscroll-table
  width: 100%
  height: 100%
  .q-table__top,
  .q-table__bottom,
  thead tr:first-child th
    background-color: #fff
  thead tr th
    position: sticky
    z-index: 1
  thead tr:last-child th
    top: 48px
  thead tr:first-child th
    top: 0


</style> -->

<script>
import { defineComponent, ref } from "vue";
import { api, llamaServer } from "boot/axios";

// import * as XLSX from 'xlsx';

const patientColumns = [
  // { name: 'document_id', label: 'id', field: 'document_id', required: true, sortable: false, align: 'left'},
  {
    name: "context",
    label: "",
    field: "context",
    required: true,
    sortable: false,
    align: "left",
  },
  // { name: 'inclusion', label: 'inclusion', field: 'inclusion', required: true, sortable: false, align: 'left'},
  // { name: 'text', label: 'text', field: 'text', required: false, sortable: false, align: 'left'}
];

const patientColumns1 = [
  {
    name: "inclusion",
    label: "inclusion",
    field: "text",
    required: true,
    sortable: false,
    align: "left",
  },
];

const visiblePatientColumns = [
  "document_id",
  "context",
  //   'inclusion'
];
const visiblePatientColumns1 = ["inclusion"];
const chatConfig = {
  chatLineColor: {
    assistant: "purple-4",
    user: "teal-4",
  },
  chatLinePosition: {
    assistant: "begin",
    user: "end",
  },
};

const chatPrompts = {
  assistente: [
    {
      role: "system",
      content:
        "Questa è una conversazione tra un utente umano e un assistente artificiale esperto di medicina. L'assistente è empatico ed educato. L'assistente parla in italiano e risponde alle domande in italiano. L'assistente è qui per rispondere alle domande, fornire consigli e aiutare l'utente a prendere decisioni. L'assistente è tenuto a rispondere a domande o task riguardanti i testi clinici al meglio delle sue possibilità.  Le risposte sono coincise ed esaustive.",
    },
  ],
};

const initChatHistory = {
  default: [
    {
      content: "Ciao sono il tuo assistente come posso aiutarti?",
      role: "assistant",
    },
  ],
};

export default defineComponent({
  name: "ChatBot",
  props: {
    inputLetter: {
      type: String,
      required: true,
    },
    inputMode: {
      type: String,
      required: true,
    },
  },
  emits: ["update:inputMode", "update:inputLetter"],
  data() {
    return {
      selectedRow: null,
      inputText: ref(""),
      chatPrompts,
      initChatHistory,
      loadingChatBot: ref(false),
      loadingChatResponse: ref(false),
      chatConfig,
      chatHistory: ref(JSON.parse(JSON.stringify(initChatHistory["default"]))),
      visiblePatientColumns,
      visiblePatientColumns1,
      patientColumns,
      patientColumns1,
      loadingPatientSearch: ref(false),
      patientSearchText: ref(""),
      patientResults: ref([]),
      loadingCriteriaCheck: ref(false),
      criteriacheckText: ref(""),
      criteriaResults: ref([]),
      inputModeLocal: "edit",
      inputLetterLocal: "",
    };
  },
  computed: {
    combinedResults() {
      const combined = [];
      const maxLength = 100; // Adjust this value to your desired length

      function truncateText(text, maxLength) {
        if (text.length <= maxLength) {
          return text;
        }
        return text.substring(0, maxLength) + "...";
      }

      // Process patientResults
      this.patientResults.forEach((result, index) => {
        const row = {};
        let idString = `<strong>PatientID</strong>: ${result.document_id}`;
        let truncatedText = truncateText(result.text, maxLength);
        let contextString = `<strong>Context</strong>: ${truncatedText}`;
        row.context = `${idString}<br>${contextString}`;
        row.text = this.patientResults[index].text;
        if (this.criteriaResults[index]) {
          let inclusionString = `<strong>Elegiblity</strong>: ${this.criteriaResults[index].text}`;
          row.context = `${idString}<br>${contextString}<br>${inclusionString}`;
          row.inclusion = this.criteriaResults[index].text;
        }
        combined.push(row);
      });

      // Process criteriaResults
      // this.criteriaResults.forEach((result, index) => {
      //   const row = {};
      //   row.id = 'id';
      //   row.context = 'context';
      //   row.inclusion = 'Inclusion'; // Title for inclusion value
      //   row.idValue = this.patientResults[index].document_id;
      //   row.contextValue = this.patientResults[index].context;
      //   row.inclusionValue = result.text;
      //   combined.push(row);
      // });

      return combined;
    },
  },
  methods: {
    async sendMessage(myText) {
      // let currentChat = null
      // if (this.attached){
      //   currentChat = [
      //     { content: 'Questo è il testo clinico allegato. TESTO ALLEGATO: ```' + this.attachedDocument + '```' , role: "user" },
      //     { content: myText, role: "user" }
      //   ]
      // } else {
      //   currentChat = [{ content: myText, role: "user" }]
      // }
      // console.log(currentChat)
      let currentChat = [{ content: myText, role: "user" }];

      this.loadingChatResponse = true;
      this.$refs.chatWindow.scrollTop = this.$refs.chatWindow.scrollHeight;
      if (myText === "") return;
      this.chatHistory = this.chatHistory.concat(currentChat);
      this.inputText = "";
      this.chatHistory.push({
        content: "...",
        role: "assistant",
      });
      this.$nextTick(() => {
        this.$refs.chatWindow.scrollTop = this.$refs.chatWindow.scrollHeight;
      });
      // this.chatHistory.slice(-1)[0]['content'] = ''
      fetch(llamaServer + "/v1/chat/completions", {
        // fetch('http://localhost:51124/v1/chat/completions', {
        method: "POST",
        body: JSON.stringify({
          messages: this.chatPrompts["assistente"].concat(this.chatHistory),
          stream: true,
          temperature: 0,
          max_tokens: 500,
          //  top_p: 0,
          //  top_k: 0,
          //  mirostat_tau: 3.0,
          //  repeat_penalty: 1.1
        }),
        headers: {
          "Content-Type": "application/json",
          timeout: 36000,
        },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Errore nella chiamata POST");
          }
          return response.body;
        })
        .then((body) => {
          const reader = body.getReader();
          const processStream = ({ done, value }) => {
            if (done) {
              console.log("Stream di eventi completato");
              this.loadingChatResponse = false;
              return;
            }
            let chunkRaw = new TextDecoder().decode(value);
            // console.log(chunkRaw)
            const chunkArray = chunkRaw.split("data:").slice(1);

            for (let chunk of chunkArray) {
              try {
                chunk = JSON.parse(chunk.split(": ping -")[0]);
                // console.log(chunk)
              } catch {
                console.log("il parsing non è andato a buon fine");
                console.log(chunk);
              }
              if (Object.keys(chunk).includes("choices")) {
                if (
                  Object.keys(chunk["choices"][0]["delta"]).includes("role")
                ) {
                  this.chatHistory.slice(-1)[0]["role"] =
                    chunk["choices"][0]["delta"]["role"];
                  this.chatHistory.slice(-1)[0]["content"] = "";
                } else {
                  this.chatHistory.slice(-1)[0]["content"] += chunk[
                    "choices"
                  ][0]["delta"]["content"]
                    ? chunk["choices"][0]["delta"]["content"]
                    : "";
                  // Gestisci il chunk di evento ricevuto dallo stream
                  this.$nextTick(() => {
                    this.$refs.chatWindow.scrollTop =
                      this.$refs.chatWindow.scrollHeight;
                  });
                }
              }
            }
            return reader.read().then(processStream);
          };

          reader.read().then(processStream);
        })
        .catch((error) => {
          this.chatHistory.slice(-1)[0]["content"] =
            "Si è verificato un errore controlla che il testo non sia troppo lungo";
          console.error(
            "Si è verificato un errore durante la chiamata POST:",
            error
          );
          this.loadingChatResponse = false;
        });
    },
    loadChatBot() {
      this.resetChatHistory();
      // this.loadingChatBot = true

      // const modelName = this.modelConfig[this.setupName].modelName
      // api.get('/get_chatbot_name').then( (response) => {
      //   if (response.data.model_name !== modelName) {
      //     api.post('/set_chatbot_model', {model_name: modelName}).then((response)=> {
      //       this.loadingChatBot = false
      //     })
      //   }else{
      //     this.loadingChatBot = false
      //   }

      // }).catch( (error) => {
      //   error.message
      //   this.loadingChatBot = false
      // })
    },
    resetChatHistory() {
      this.chatHistory = JSON.parse(
        JSON.stringify(this.initChatHistory["default"])
      );
    },
    attachDocument() {
      if (this.inputLetter != null && this.inputLetter != "")
        this.attachedDocument = this.inputLetter;
      this.chatHistory.push({
        content:
          "Rispondi alle domande relative al seguente Testo Clinico: ```" +
          this.attachedDocument +
          "```",
        role: "user",
        visible: false,
      });
      this.loadingChatResponse = true;
      fetch(llamaServer + "/v1/chat/completions", {
        // fetch('http://131.175.15.22:61111/hbd-demo-api/send_message/', {
        method: "POST",
        body: JSON.stringify({
          messages: this.chatPrompts["assistente"].concat(this.chatHistory),
          stream: true,
          temperature: 0,
          max_tokens: 1,
          // top_p: 0,
          // top_k: 0,
          // mirostat_tau: 0,
          // repeat_penalty: 1.1
        }),
        headers: {
          "Content-Type": "application/json",
          timeout: 36000,
        },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Errore nella chiamata POST");
          }
          return response.body;
        })
        .then((body) => {
          const reader = body.getReader();
          const processStream = ({ done, value }) => {
            if (done) {
              console.log("Caricamento allegato completato");
              this.loadingChatResponse = false;
              return;
            }
            return reader.read().then(processStream);
          };
          reader.read().then(processStream);
        });
    },
    //////////////////////////////////////////////////////
    selectRow(index) {
      this.selectedRow = index; // Set selectedRow to index of clicked row
    },
    attachCriteria(row) {
      console.log("attach called with:", row);
      const txt = row.text;
      this.$emit("update:inputLetter", txt);
      this.$emit("update:inputMode", "edit");
      this.dropzoneURL = "";
      const text = this.criteriacheckText;
      if (text != null && text.trim() !== "") {
        const criteriaText = text.trim();
        const criteriaResult = row.inclusion.trim();
        const CriteriaMessage = `Given the clinical text and the following eligibility inclusion criteria for a clinical trial:
              (${criteriaText})
              Determined the patient:
              (${criteriaResult})`;
        this.chatHistory.push({ content: CriteriaMessage, role: "user" });
      } else {
        this.chatHistory.push({
          content:
            "Rispondi alle domande relative al seguente Testo Clinico: ```" +
            txt +
            "```",
          role: "user",
        });
      }

      this.loadingChatResponse = true;
      fetch(llamaHost + "/v1/chat/completions", {
        // fetch('http://131.175.15.22:61111/hbd-demo-api/send_message/', {
        method: "POST",
        body: JSON.stringify({
          messages: this.chatPrompts["assistente"].concat(this.chatHistory),
          stream: true,
          temperature: 0,
          max_tokens: 1,
          // top_p: 0,
          // top_k: 0,
          // mirostat_tau: 0,
          // repeat_penalty: 1.1
        }),
        headers: {
          "Content-Type": "application/json",
          timeout: 36000,
        },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Errore nella chiamata POST");
          }
          return response.body;
        })
        .then((body) => {
          const reader = body.getReader();
          const processStream = ({ done, value }) => {
            if (done) {
              console.log("Caricamento allegato completato");
              this.loadingChatResponse = false;
              return;
            }
            return reader.read().then(processStream);
          };
          reader.read().then(processStream);
        });
    },
    //////////////////////////////////////////////////////
    searchPatient() {
      this.loadingPatientSearch = true;
      api
        .post("/patient_search", { query: this.patientSearchText })
        .then((response) => {
          console.log(response.data);
          this.loadingPatientSearch = false;
          this.patientResults = response.data.output;
        })
        .catch((error) => {
          console.log("error with patient search call:", error.message);
          this.loadingPatientSearch = false;
        });
      // Clear the criteriaResults array when the patient search is done
      this.criteriaResults = [];
    },

    criteriaCheck() {
      this.loadingCriteriaCheck = true;
      api
        .post("/criteria_check", { criteria: this.criteriacheckText })
        .then((response) => {
          console.log(response.data);
          this.loadingCriteriaCheck = false;
          this.criteriaResults = response.data.criteria;
        })
        .catch((error) => {
          console.log("error with criteria check:", error.message);
          this.loadingCriteriaCheck = false;
        });
    },

    showRetrievedDocument(text) {
      this.$emit("update:inputLetter", text);
      this.$emit("update:inputMode", "edit");
      this.dropzoneURL = "";
    },
    updateTaskName() {
      this.setupName = null;
      this.taskName = this.taskName.value;
    },
  },
});
</script>
