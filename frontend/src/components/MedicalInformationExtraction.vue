<script>
import {ref} from "vue";
import {llamaHost} from "boot/axios";
import {v4 as uuidv4} from 'uuid';


/* prettier-ignore */
/* @formatter:off */
 const columns = [
   {name: 'name', label: 'Name', field: 'name', align: 'left', sortable: true},
   {name: 'dose', label: 'Dose', field: 'dose', align: 'left', sortable: true},
   {name: 'frequency', label: 'Frequency', field: 'frequency', align: 'left', sortable: true},
   {name: 'route', label: 'Route', field: 'route', align: 'left', sortable: true},
]

 const rows = [

 ]
/* @formatter:on */
export default {
  name: "MedicationExtractionChat",
  emits: ['request-text'],
  data() {
    return {
      table: ref({
        columns: columns,
        rows: rows,
      }),
      chat: ref({
        modelParameters: [
          {
            name: "context",
            placeholder: "Context",
            type: "number",
            model: ref(4096),
          },
          {
            name: "n-predict",
            placeholder: "N predict",
            type: "number",
            model: ref(512),
          },
          {
            name: "temperature",
            placeholder: "Temperature",
            type: "float",
            model: ref(0),
          },
          {
            name: "top_p",
            placeholder: "Top_p",
            type: "float",
            model: ref(0),
          },
          {
            name: "top_k",
            placeholder: "Top_k",
            type: "number",
            model: ref(0),
          },
          {
            name: "mirostat_tau",
            placeholder: "Mirostat_tau",
            type: "float",
            model: ref(3.0),
          },
          {
            name: "penalty",
            placeholder: "Repeat penalty",
            type: "float",
            model: ref(1.1),
          },

        ],
        text: ref(""),
        textPiecesCount: ref(0),
        chat: ref([]),
      }),
      tab: ref('chat'),
      loadingChatResponse: ref(false),
      showTemplate: ref(false),
      completionInit: ref(''),
      prompt: ref(""),
      template: '<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n{completion_init}',
      iterationTemplate: '<|im_start|>{{role}}\n{{content}}<|im_end|>\n',
      systemMessage: ref(`Emulate a tool for the specified task. Strictly follow the provided instructions to execute the task accurately. Your role is to adhere solely to the given guidelines and perform the designated actions without deviation.`),
      shrinkPrompt: ref(false),
      multipleSystemMessages: ref(false),
      counter: ref(0),
      rawText: ref(true),
    }
  },
  methods: {
    parseAnswer(answer) {
      let table = []
      let lines = answer.split('\n')
      console.log(lines)
      for (let line of lines) {
        if (line.match(/.*?(OUTPUT|END).*?/g)) {
          break
        }
        if (line.includes('||')) {
          let row = line.split('||')
          table.push({
            name: row[0],
            dose: row[1],
            frequency: row[2],
            route: row[3],
          })

        } else {
          console.log('line not parsed', line)
        }
      }
      console.log(table)
      this.table.rows = table


    },
    requestText() {
      this.$emit('request-text')
    },


    prepareChat() {
      let editableDiv = this.$refs.userMessage;
      if (!editableDiv) return;
      editableDiv.addEventListener('keydown', function (e) {
        let restoredDivs = document.querySelectorAll('[data-warning-delete=true]');
        if (e.key !== 'Backspace' && e.key !== 'Delete')
          for (let restoredDiv of restoredDivs) {
            restoredDiv.setAttribute('data-warning-delete', 'false');
            restoredDiv.style.backgroundColor = '#EEEEEEFF'
          }
        if (e.key === 'Backspace' && window.getSelection().anchorOffset === 0) {
          let prevEl = window.getSelection().anchorNode.previousElementSibling
          if (prevEl && prevEl.getAttribute('contenteditable') === 'false') {
            if (prevEl.getAttribute('data-warning-delete') === 'false') {
              prevEl.setAttribute('data-warning-delete', 'true');
              prevEl.style.backgroundColor = '#BDBDBDFF'

              e.preventDefault();
            }
          }
        }
        if (e.key === 'ArrowDown') {
          console.log('arrow down')
          let nextEl = window.getSelection().anchorNode.nextElementSibling
          console.log(nextEl)
          if (nextEl && nextEl.getAttribute('data-section-type') === 'file'
            && !nextEl.nextSibling) {
            nextEl.outerHTML += '\n'
          }
        }
      });
    },
    animateScroll() {
      this.$refs.scrollAreaRef.scrollTo({top: this.$refs.scrollAreaRef.scrollHeight, behavior: 'smooth'})
    },
    convertChatToCompletionFormat() {
      let content = ''
      this.chat.chat.slice(0, -1).forEach(message => {
        content += this.iterationTemplate.replace('{{role}}', message.sender)
          .replace('{{content}}', message.message)
      })
      content += this.iterationTemplate.replace('{{role}}', 'assistant')
        .split("{{content}}")[0] + this.completionInit
      return content
    },
    clearChat() {
      this.chat.chat = this.chat.chat.filter(el => el.sender === 'ctx')
    },
    buildUserMessage() {
      if (this.rawText)
        return this.$refs.userMessage.innerText;
      let div = this.$refs.userMessage
      let prompt = ''
      let childNodes = Array.from(div.childNodes);
      for (let child of childNodes) {
        if (child.nodeType === 1 && child.getAttribute('data-section-type') === 'file') {
          prompt += child.querySelector('[data-section-file-content]').innerText
        } else {
          prompt += child.textContent
        }
        prompt += '\n'
      }
      prompt.trim()
      return prompt
    },
    attach(fileName, fileContent) {
      if (this.rawText) {
        this.$refs.userMessage.innerText += fileContent + '\n'
        return
      }
      let el
      if (window.getSelection().anchorNode && window.getSelection().anchorNode.parentNode === this.$refs.userMessage) {
        console.log('anchor node', window.getSelection().anchorNode)
        el = window.getSelection().anchorNode
      } else {
        if (this.$refs.userMessage.childNodes.length === 0)
          this.$refs.userMessage.innerText = "\n"
        el = this.$refs.userMessage.children[this.$refs.userMessage.childNodes.length - 1]
      }
      let div = document.createElement('div')
      div.setAttribute('contenteditable', 'false')
      div.setAttribute('data-section-type', 'file')
      div.setAttribute('data-warning-delete', 'false')
      div.classList.add('q-pa-sm', 'no-border', 'rounded-borders')
      div.style.maxWidth = '400px'
      div.style.height = '4rem'
      div.style.backgroundColor = '#EEEEEEFF'
      div.innerHTML = '<div data-section-file-name>' + fileName + '</div>' +
        '<p data-section-file-content ' +
        'style="width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">' + fileContent + '</p>'
      el.after(div)

    },

    async sendMessage() {
      if (!this.rawText)
        if (!this.multipleSystemMessages && this.chat.chat.find(el => el.sender === 'system'))
          this.chat.chat.find(el => el.sender === 'system').message = this.systemMessage
        else
          this.chat.chat.push({
            id: uuidv4(),
            sender: 'system',
            message: this.systemMessage,
            expand: false,
          })

      this.chat.chat.push({
        id: uuidv4(),
        sender: 'user',
        message: this.buildUserMessage(),
        expand: false,
      }, {
        id: uuidv4(),
        sender: 'assistant',
        message: this.completionInit,
        expand: false,
      })
      let promptToSend = this.rawText ? this.buildUserMessage() : this.convertChatToCompletionFormat();
      this.loadingChatResponse = true
      this.$refs.userMessage.innerHTML = ''
      fetch(llamaHost + '/v1/completions', {
        method: 'POST',
        body: JSON.stringify({
          prompt: promptToSend,
          max_tokens: 1024,
          stream: true,
          stop: ['<|im_end|>'],
          temperature: 0.8,
          // top_p: 0,
          // top_k: 0,
          mirostat_tau: 8.0,
          // repeat_penalty: 1.1
        }),
        headers: {
          'Content-Type': 'application/json',
          timeout: 36000
        }
      })
        .then(response => {
          const reader = response.body.getReader();
          const processStream = ({done, value}) => {
            if (done) {
              this.loadingChatResponse = false

              return;
            }
            let chunkRaw = new TextDecoder().decode(value);
            const chunkArray = chunkRaw.split('data:').slice(1)
            for (let chunk of chunkArray) {
              try {
                chunk = JSON.parse(chunk.split(': ping -')[0])

                this.chat.chat.slice(-1)[0].message
                  += chunk['choices'][0]['text']
              } catch {
                console.log('il parsing non è andato a buon fine')
              }

            }


            this.$nextTick(() => {
              this.animateScroll()
            });
            return reader.read().then(processStream);
          };

          reader.read().then(processStream);

        })
        .catch(error => {
          console.error(error);
          this.loadingChatResponse = false
          return error.body;
        })
        .catch(error => {
          this.chatHistory.slice(-1)[0]['content'] = 'Si è verificato un errore controlla che il testo non sia troppo lungo'
          console.error('Si è verificato un errore durante la chiamata POST:', error);
          this.loadingChatResponse = false
        });


    },

  },
  mounted() {
    this.prepareChat();
  }
}
</script>

<template>
  <q-card class="relative-position"
          style="height: 90%"
  >
    <div v-if="loadingChatResponse === true"
         class="absolute-top-left bg-grey-3 row justify-center items-center"
         style="height: 100%; width: 100%; z-index: 10; opacity: 50%">
      <q-spinner-gears
        color="primary"
        size="8em"
      />

    </div>
    <q-card style="max-height: 100%" class="full-height column full-width no-wrap">
      <q-tabs class="text-grey"
              v-model="tab"
              dense
              active-color="primary"
              indicator-color="primary"
              align="justify"
              narrow-indicator
      >
        <q-tab name="chat" label="Chat"/>
        <q-tab name="table" label="Table"/>
      </q-tabs>
      <q-separator class="bi-border"/>
      <q-tab-panels v-model="tab" animated class="column no-wrap overflow-hidden "
                    style="height: 100%"
                    @transition=" prepareChat()"
      >
        <q-tab-panel class="overflow-hidden" name="chat"
                     style="height: 100%"
        >
          <div class="full-height column justify-between full-width no-wrap overflow-auto">
            <!--     Model Settings       -->
            <q-expansion-item class="q-pb-md bg-grey-3"
                              expand-separator
                              icon="settings"
                              label="Model Parameters"
            >
              <q-card class="q-pa-none">
                <q-card-section class="q-pa-none flex justify-start">
                  <q-input
                    v-for="param in chat.modelParameters" :key="param"
                    v-model="param.model"
                    :type="param.type === 'float' ? 'number' : param.type"
                    :step="param.type === 'float' ? '0.01' : ''"
                    :label="param.placeholder"
                    style="width: 48%"
                    class="q-pa-none"
                  />
                </q-card-section>
              </q-card>
            </q-expansion-item>
            <div class="overflow-auto items-center col column no-wrap full-width "
                 ref="scrollAreaRef"
            >
              <div style="width: 95%; white-space: pre-line" class="q-py-sm"
                   v-for="message in chat.chat"
                   :key="message.id"
              >
                <div v-if="message.sender === 'system'" class="rounded-borders q-pa-sm bg-grey-3 "
                >
                  {{ message.message }}
                </div>
                <q-chat-message
                  style="width: 70%"
                  :class="{'q-ml-auto': message.sender === 'user', 'q-mr-auto': message.sender === 'assistant'}"
                  v-else
                  :sent="message.sender === 'user'"
                >
                  <div class="flex items-end justify-end overflow-hidden no-wrap"
                       :style="{maxHeight: message.expand?'unset':'100px'}">
                    <span v-if="showTemplate">
                      {{
                        iterationTemplate.replace("\{\{role\}\}", message.sender).replace("\{\{content\}\}", message.message)
                      }}
                    </span>

                    <span v-else>{{ message.message }}</span>
                    <q-btn class=""
                           round dense flat :icon="message.expand?'expand_less':'expand_more'"
                           @click="message.expand =!message.expand"/>

                  </div>
                </q-chat-message>
              </div>
            </div>
            <q-separator class="q-mt-md"></q-separator>
            <div class="flex justify-end">
              <q-icon class="q-mx-sm" :name="shrinkPrompt?'expand_less':'expand_more'" size="2em" color="grey-5"
                      @click="shrinkPrompt =!shrinkPrompt"/>
            </div>
            <div class="flex row" :class="{'col-2':shrinkPrompt}"
            >
              <div class="col-12 bg-grey-3 rounded-borders overflow-scroll column"
              >
                <div class="col-grow flex q-pa-sm rounded-borders justify-between bg-grey-4">
                  <div class="flex no-wrap">
                    <q-btn class="q-mx-sm" round dense flat icon="attach_file"
                           @click="requestText()"/>
                    <q-btn class="q-mx-sm" round dense flat :icon="rawText?'raw_on':'raw_off'"
                           @click="rawText = !rawText"/>
                    <q-btn class="q-mx-sm" round dense flat :icon="this.showTemplate?'visibility':'visibility_off'"
                           @click="showTemplate = !showTemplate" :disable="rawText"/>


                    <q-checkbox v-model="multipleSystemMessages" label="Multiple System Messages"></q-checkbox>
                  </div>
                  <div style="display: flex;">
                    <q-btn class="q-mx-sm" round dense flat icon="cleaning_services" @click="clearChat()"/>
                    <q-btn class="q-mx-sm" round dense flat icon="send" @click="sendMessage()"/>
                  </div>
                </div>
                <q-separator></q-separator>

                <div class="q-pa-sm col overflow-auto">
                  <div v-show="showTemplate && !rawText">
                    <p style="margin: 0">
                      {{ this.template.slice(0, this.template.indexOf('{system_message}') - 1) }}</p>
                    <textarea class="bg-white q-pa-sm no-border rounded-borders full-width"
                              style="resize: none"
                              placeholder="System message"
                              v-model="this.systemMessage"
                    />
                    <p style="margin: 0"
                       v-html="this.template.slice(this.template.indexOf('{system_message}')+16, this.template.indexOf('{prompt}')-1)
                      .replace('\n', '<br>')"
                    ></p>

                  </div>
                  <div style="position: relative; max-height: 400px">
                    <div data-ph="Prompt"
                         class="q-pa-sm no-border rounded-borders full-width bg-white"
                         style="resize: none; white-space: pre-line; min-height: 1rem; display:inline-block;"
                         ref="userMessage"
                         contenteditable="true"
                    >
                    </div>
                  </div>
                  <div v-show="showTemplate && !rawText">
                    <p style="margin: 0"
                       v-html="this.template.slice(this.template.indexOf('{prompt}')+8, this.template.indexOf('{completion_init}')-1)
                      .replace('\n', '<br>')"
                    ></p>
                    <textarea contenteditable="true" class="bg-white q-pa-sm no-border rounded-borders full-width"
                              style="resize: none"
                              placeholder="Completion init"
                              v-model="this.completionInit"
                    />
                  </div>
                </div>
              </div>

            </div>
          </div>
        </q-tab-panel>


        <q-tab-panel name="table" class="column" style="height: 100%">
          <div class="text-h6">Table</div>
          <q-btn
            class="q-ma-sm" color="primary"
            @click="parseAnswer(chat.chat.slice(-1)[0].message)"
          >Parse last Answer
          </q-btn>
          <q-table
            style="max-height: 600px"
            class="col"
            title="Medications"
            :rows="table.rows"
            :columns="table.columns"
            row-key="name"
            :rows-per-page-options="[0, 10, 20, 30]"
          />
        </q-tab-panel>

      </q-tab-panels>
    </q-card>

    <q-separator/>
  </q-card>

</template>

<style scoped lang="scss">
[contenteditable=true]:empty:not(:focus):before {
  content: attr(data-ph);
  color: grey;
}

[data-section-file-name]:before {
  content: 'File Name: ';
  font-weight: bold;
}

[data-section-file-content]:before {
  content: 'File Content: ';
  font-weight: bold;
}

div[data-warning-delete=false] {
  background: $grey-3 !important;
}

div[data-warning-delete=true] {
  background: #BDBDBDFF !important;
}


</style>