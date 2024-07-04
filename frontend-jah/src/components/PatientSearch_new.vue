<template>
  <div class="row justify-evenly">
    <div class="row">
      <!-- Left Card -->
      <q-card class="column no-wrap" style="width: 50%; height: 680px;">
        <div class="row">
          <!-- PatientSearch -->
          <!-- <q-card style="width: 100%; height: 150px;"> -->
          <q-card-section class="row justify-between" >
              <div class="col-2"></div>
              <div class="text-h6 text-primary">Patient Search</div>
              <div class="col-2"></div>
            <q-card-section class="q-pt-md" style="height: 75px;">
              <div style="width: 160%;" class="q-pa-sm">
                  <div class="row no-wrap" style="width: 100%;">
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
         <!-- </q-card-section> -->
          <!-- </q-card> -->
          <!-- Search Results -->
          <!-- <q-card style="width: 100%; height: 530px; display: flex; flex-direction: column;"> -->
            <!-- <q-card-section class="row justify-between"> -->
            <div class="col-2"></div>
            <div class="text-h6 text-primary">Search Results:</div>
            <div class="col-2"></div>
            <div class="q-pt-md" style="display: flex; justify-content: space-between;">
              <div class="table-container" style="height: 490px;">
                <q-table
                  class="my-sticky-virtscroll-table"
                  :rows-per-page-options="[0]"
                  table-header-style="text-align: left"
                  table-header-class="align-left text-primary text-bold"
                  wrap-cells
                  dense
                  separator="cell"
                  :columns="patientColumns"
                  :rows="combinedResults"
                  :loading="loadingPatientSearch || loadingCriteriaCheck"
                  style="width: 450px; table-layout: fixed;"
                  @row-click="handleRowClick"
                >
                  <template v-slot:loading>
                    <q-inner-loading showing color="primary" />
                  </template>
                  <!-- <template v-slot:body-cell="props">
                    <q-td :props="props">
                        <span style="cursor: pointer" @click="showRetrievedDocument(props.row.text)">{{ props.value }}</span>
                    </q-td>
                  </template> -->
                  <template v-slot:body-cell-context="props">
                    <q-td :props="props">
                      <pre style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer;" 
                      v-html="props.value" @click="showRetrievedDocument(props.row.text)"></pre>
                    </q-td>
                  </template>
                </q-table>
              </div> 
            </div> 
            </q-card-section>
          <!-- </q-card> -->
        </div>  
      </q-card>
      <!-- Middle Card -->
      <q-card class="column no-wrap" style="width: 50%; height: 680px;">
        <div class="row">
          <!-- Inclusion/Exclusion Criteria -->
          <q-card style="width: 100%; height: 250px;">
            <q-card-section class="row justify-between" style="height: 5%">
              <div class="col-2"></div>
              <div class="text-h6 text-primary">Inclusion/Exclusion Criteria</div>
              <div class="col-2"></div>
            </q-card-section>
            <q-card-section class="" style="height: 80%;">
              <div style="width: 100%;" class="q-pa-sm">
                  <div class="q-pa-sm" style="width: 100%;">
                    <q-input
                      style="width: 100%; max-height: 150px;"  
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
          <q-card style="width: 100%; height: 430px;">
            <q-card-section class="row justify-between" style="height: 5%">
              <div class="col-2"></div>
              <div class="text-h6 text-primary">ChatBot Output</div>
              <div class="col-2"></div>
            </q-card-section>
            <q-card-section class="" style="height: 90%">
              <div v-if="loadingChatBot" class="column justify-center items-center no-wrap col-12" style="height: 100%">
                  <q-spinner color="primary" size="6em" />
                  </div>
                  <div v-if="!loadingChatBot" class="column justify-center items-center no-wrap col-12" style="height: 100%">
                  <div class="row justify-start items-center" style="width: 100%">
                  </div>
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
                              style="border-radius: 12px; width: fit-content; max-width: 60%; white-space: pre-line;"
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
                      @keyup.enter="loadingChatResponse ? true : sendMessage(inputText) "
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

<style lang="sass">
.my-sticky-virtscroll-table
  /* height or max-height is important */
  width: 95%
  height: 490px

  .q-table__top,
  .q-table__bottom,
  thead tr:first-child th /* bg color is important for th; just specify one */
    background-color: #fff

  thead tr th
    position: sticky
    z-index: 1
  /* this will be the loading indicator */
  thead tr:last-child th
    /* height of all previous header rows */
    top: 48px
  thead tr:first-child th
    top: 0
</style>
  
<script>
import { defineComponent, ref } from 'vue'
import {patientSearchApi} from "boot/axios";
import {criteriacheckApi} from "boot/axios";
import {api, llamaHost} from "boot/axios";

const patientColumns = [
// { name: 'document_id', label: 'id', field: 'document_id', required: true, sortable: false, align: 'left'},
{ name: 'context', label: '', field: 'context', required: true, sortable: false, align: 'left'},
// { name: 'inclusion', label: 'inclusion', field: 'inclusion', required: true, sortable: false, align: 'left'},
// { name: 'text', label: 'text', field: 'text', required: false, sortable: false, align: 'left'}
]

const patientColumns1 = [
{ name: 'inclusion', label: 'inclusion', field: 'text', required: true, sortable: false, align: 'left'}
]

const visiblePatientColumns = [
  'document_id',
  'context'
//   'inclusion'
]
const visiblePatientColumns1 = [
  'inclusion'
]
const chatConfig = {
  chatLineColor: {
    assistant: "purple-4",
    user: "teal-4",
  },
  chatLinePosition: {
    assistant: "begin",
    user: "end",
  },
}

const chatPrompts = {
  assistente: [
    {
      role: 'system',
      content: "Questa è una conversazione tra un utente umano e un assistente artificiale esperto di medicina. L'assistente è empatico ed educato. L'assistente parla in italiano e risponde alle domande in italiano. L'assistente è qui per rispondere alle domande, fornire consigli e aiutare l'utente a prendere decisioni. L'assistente è tenuto a rispondere a domande o task riguardanti i testi clinici al meglio delle sue possibilità.  Le risposte sono coincise ed esaustive."
    }
  ]
}

const initChatHistory = {
  default: [
    { content: "Ciao sono il tuo assistente come posso aiutarti?", role: "assistant" }
  ],
}

export default defineComponent({
    name: 'ChatBot',
    props: {
        inputLetter: {
            type: String,
            required: true
        },
        inputMode: {
            type: String,
            required: true
        }
    },
    emits:['update:inputMode', 'update:inputLetter'],
    data () {
        return {
            inputText: ref(""),
            chatPrompts,
            initChatHistory,
            loadingChatBot: ref(false),
            loadingChatResponse: ref(false),
            chatConfig,
            chatHistory: ref(JSON.parse(JSON.stringify(initChatHistory['default']))),
            visiblePatientColumns,
            visiblePatientColumns1,
            patientColumns,
            patientColumns1,
            loadingPatientSearch: ref(false),
            patientSearchText: ref(''),
            patientResults: ref([]),
            loadingCriteriaCheck: ref(false),
            criteriacheckText: ref(''),
            criteriaResults: ref([]),
            inputModeLocal: 'edit', 
            inputLetterLocal: '',
        } 
    },
    computed: {
      combinedResults() {
        const combined = [];

        // Process patientResults
        this.patientResults.forEach((result, index) => {
          const row = {};
          let idString = `<strong>PatientID:</strong>: ${result.document_id}`;
          let contextString = `<strong>Context</strong>: ${result.context}`;
          row.context = `${idString}<br>${contextString}`;
          row.text = this.patientResults[index].text;
          if (this.criteriaResults[index]) {
            let inclusionString = `<strong>Chatbot</strong>: ${this.criteriaResults[index].text}`;
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
      }
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
      let currentChat = [{ content: myText, role: "user" }]
      
      this.loadingChatResponse = true
      this.$refs.chatWindow.scrollTop = this.$refs.chatWindow.scrollHeight;
      if (myText === "") return;
      this.chatHistory = this.chatHistory.concat(currentChat);
      this.inputText = "";
      this.chatHistory.push({
        content: '...',
        role: "assistant",
      });
      this.$nextTick(() => {
          this.$refs.chatWindow.scrollTop =
          this.$refs.chatWindow.scrollHeight;
      });
      // this.chatHistory.slice(-1)[0]['content'] = ''
      fetch(llamaHost + '/v1/chat/completions', {
      // fetch('http://localhost:51124/v1/chat/completions', {
        method: 'POST',
        body: JSON.stringify({
          messages: this.chatPrompts['assistente'].concat(this.chatHistory),
          stream: true,
          temperature: 0,
          max_tokens: 500,
        //  top_p: 0,
        //  top_k: 0,
        //  mirostat_tau: 3.0,
        //  repeat_penalty: 1.1

        }),
        headers: {
          'Content-Type': 'application/json',
          timeout: 36000
        }
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Errore nella chiamata POST');
          }
          return response.body;
        })
        .then(body => {
          const reader = body.getReader();
          const processStream = ({ done, value }) => {
            if (done) {
              console.log('Stream di eventi completato');
              this.loadingChatResponse = false
              return;
            }
            let chunkRaw = new TextDecoder().decode(value);
            // console.log(chunkRaw)
            const chunkArray = chunkRaw.split('data:').slice(1)

            for (let chunk of chunkArray) {
              try {
                chunk = JSON.parse(chunk.split(': ping -')[0])
                // console.log(chunk)
              }
              catch {
                console.log('il parsing non è andato a buon fine')
                console.log(chunk)
              }
              if (Object.keys(chunk).includes('choices')) {
                if (Object.keys(chunk['choices'][0]['delta']).includes('role')) {
                  this.chatHistory.slice(-1)[0]['role'] = chunk['choices'][0]['delta']['role']
                  this.chatHistory.slice(-1)[0]['content'] = ''
                } else {
                this.chatHistory.slice(-1)[0]['content'] += chunk['choices'][0]['delta']['content'] ? chunk['choices'][0]['delta']['content'] : ''
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
        .catch(error => {
          this.chatHistory.slice(-1)[0]['content'] = 'Si è verificato un errore controlla che il testo non sia troppo lungo'
          console.error('Si è verificato un errore durante la chiamata POST:', error);
          this.loadingChatResponse = false
        });

    },
    loadChatBot () {
      this.resetChatHistory()
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
    resetChatHistory () {
      this.chatHistory = JSON.parse(JSON.stringify(this.initChatHistory['default']))
    },
    attachDocument () {
      if (this.inputLetter != null && this.inputLetter != '') 
        this.attachedDocument = this.inputLetter
        this.chatHistory.push({ content: 'Rispondi alle domande relative al seguente Testo Clinico: ```' + this.attachedDocument + '```' , role: "user" })
        this.loadingChatResponse = true
        fetch(llamaHost + '/v1/chat/completions', {
          // fetch('http://131.175.15.22:61111/hbd-demo-api/send_message/', {
          method: 'POST',
          body: JSON.stringify({
            messages: this.chatPrompts['assistente'].concat(this.chatHistory),
            stream: true,
            temperature: 0,
            max_tokens: 1,
            // top_p: 0,
            // top_k: 0,
            // mirostat_tau: 0,
            // repeat_penalty: 1.1

          }),
          headers: {
            'Content-Type': 'application/json',
            timeout: 36000
          }
        })
          .then(response => {
            if (!response.ok) {
              throw new Error('Errore nella chiamata POST');
            }
            return response.body;
          })
          .then(body => {
            const reader = body.getReader();
            const processStream = ({ done, value }) => {
              if (done) {
                console.log('Caricamento allegato completato');
                this.loadingChatResponse = false
                return;
              }
              return reader.read().then(processStream);
            }
            reader.read().then(processStream);
          })
    },
    searchPatient() {
            this.loadingPatientSearch = true;
            patientSearchApi.post(
                '/patient_search',
                { query: this.patientSearchText }
            ).then((response) => {
                console.log(response.data);
                this.loadingPatientSearch = false;
                this.patientResults = response.data.output;
            }).catch((error) => {
                console.log('error with patient search call:', error.message);
                this.loadingPatientSearch = false;
            });
            // Clear the criteriaResults array when the patient search is done
            this.criteriaResults = [];
        },
      
    criteriaCheck() {
            this.loadingCriteriaCheck = true;
            criteriacheckApi.post(
                '/criteria_check',
                { criteria: this.criteriacheckText }
            ).then((response) => {
                console.log(response.data);
                this.loadingCriteriaCheck = false;
                this.criteriaResults = response.data.criteria;
            }).catch((error) => {
                console.log('error with criteria check:', error.message);
                this.loadingCriteriaCheck = false;
            });
        },
    
    showRetrievedDocument (text) {
      this.$emit('update:inputLetter', text);
      this.$emit('update:inputMode', "edit")
      this.dropzoneURL = ''
    },
    updateTaskName () {
      this.setupName = null
      this.taskName = this.taskName.value
    },
    }
});
</script>
  