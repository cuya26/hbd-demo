<template>
  <q-card>
    <q-card-section class=" row justify-between">
      <div class="col-2"></div>
      <div class="text-h6 text-primary">Output</div>
      <div class="col-2"></div>
    </q-card-section>
    <q-card-section
      class="" style="height: 90%"
    >
      <div v-if="loadingChatBot" class="column justify-center items-center no-wrap col-12" style="height: 100%">
        <q-spinner color="primary" size="6em"/>
      </div>
      <div v-if="!loadingChatBot" class="column justify-center items-center no-wrap col-12" style="height: 100%">
        <div class="row justify-start items-center" style="width: 100%">
          <!-- <q-toggle
          v-model="attached"
          icon="attach_file"
          label="Attach Document"
          @update:model-value="attachDocument"
          /> -->

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
</template>

<script>
import {defineComponent, ref} from 'vue'
import {api, llamaHost} from "boot/axios";

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
    {content: "Ciao sono il tuo assistente come posso aiutarti?", role: "assistant"}
  ],
}

export default defineComponent({
  name: 'ChatBot',
  props: {
    inputLetter: {
      required: true
    }
  },
  data() {
    return {
      inputText: ref(""),
      chatPrompts,
      initChatHistory,
      loadingChatBot: ref(false),
      loadingChatResponse: ref(false),
      chatConfig,
      chatHistory: ref(JSON.parse(JSON.stringify(initChatHistory['default']))),
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
      let currentChat = [{content: myText, role: "user"}]
      api.post('/llama_tokenizer', {chat: this.chatPrompts['assistente'].concat(this.chatHistory).concat(currentChat)}
      ).then((response) => {
        console.log(response.data)
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
            const processStream = ({done, value}) => {
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
                } catch {
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
      })

    },
    loadChatBot() {
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
    resetChatHistory() {
      this.chatHistory = JSON.parse(JSON.stringify(this.initChatHistory['default']))
    },
    attachDocument() {
      if (this.inputLetter != null && this.inputLetter != '')
        api.post('/llama_tokenizer_filter', {text: this.inputLetter, max_length: 5500}).then((response) => {
          this.attachedDocument = response.data.text
          this.chatHistory.push({
            content: 'Rispondi alle domande relative al seguente Testo Clinico: ```' + this.attachedDocument + '```',
            role: "user"
          })
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
              const processStream = ({done, value}) => {
                if (done) {
                  console.log('Caricamento allegato completato');
                  this.loadingChatResponse = false
                  return;
                }
                return reader.read().then(processStream);
              }
              reader.read().then(processStream);
            })
        }).catch(error => {
          error.message
          console.log('errore caricamento allegato')
        })
    },
  }
})
</script>

