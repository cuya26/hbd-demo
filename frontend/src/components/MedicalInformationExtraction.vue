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
  name: "MedicationExtraction",
  props: ['doc'],
  emits: ['request-document'],
  watch: {
    doc(newValue, oldValue) {
    }
  },
  data() {
    return {
      table: ref({
        columns: columns,
        rows: rows,
      }),
      modelParameters: {
        max_tokens: {
          placeholder: "Max tokens",
          type: "number",
          model: ref(512),
        },
        temperature: {
          placeholder: "Temperature",
          type: "float",
          model: ref(0),
        },
        top_p: {
          placeholder: "Top_p",
          type: "float",
          model: ref(0),
        },
        top_k: {
          placeholder: "Top_k",
          type: "number",
          model: ref(0),
        },
        mirostat_tau: {
          placeholder: "Mirostat_tau",
          type: "float",
          model: ref(3.0),
        },
        repeat_penalty: {
          placeholder: "Repeat penalty",
          type: "float",
          model: ref(1.1),
        }
      },
      answer: ref(''),
      tab: ref('table'),
      loadingResponse: ref(false),
      showTemplate: ref(false),
      completionInit: ref('[CSV_1_START]\n' +
        'medication || dosage || mode || frequency'),

      prompt: ref(`TASK: Named Entity Medical Extraction
Extract all and only the medication, dosage, mode, frequency from the text.
Put all the extracted entities into a csv table with the columns medication and dosage.
If no data in any of the columns write "nm".
Follow a csv format, like this "medication || dosage || mode || frequency".
[CLINICAL_DOCUMENT_START]
{file}
[CLINICAL_DOCUMENT_END]`),
      template: '<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n{completion_init}',
      systemMessage: ref(`Emulate a tool for the specified task. Strictly follow the provided instructions to execute the task accurately. Your role is to adhere solely to the given guidelines and perform the designated actions without deviation.`),
      shrinkPrompt: ref(false),
    }
  },
  methods: {
    adjustHeight() {
      let editableDiv = this.$refs.userMessage;
        if (!editableDiv) return;
      editableDiv.style.height = 0 + 'px';
      editableDiv.style.height =  editableDiv.scrollHeight + "px";
    },

    parseAnswer(answer) {
      let table = []
      let lines = answer.split('\n')
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
      this.table.rows = table
    },
    applyToTemplate() {
      return this.template
        .replace('{system_message}', this.systemMessage)
        .replace('{prompt}', this.buildUserMessage())
        .replace('{completion_init}', this.completionInit)
    },
    clear() {
      this.answer = ''
    },
    buildUserMessage() {
      return this.prompt.replace('{file}', this.doc)
    },
    prepareExtraction() {
      this.adjustHeight()

    },

    async extractMedications() {
      this.loadingResponse = true
      fetch(llamaHost + '/v1/completions', {
        method: 'POST',
        body: JSON.stringify({
          prompt: this.applyToTemplate(),
          max_tokens: 1024,
          stream: true,
          stop: ['<|im_end|>'],
          temperature: this.modelParameters.temperature.model,
          top_p: this.modelParameters.top_p.model,
          top_k: this.modelParameters.top_k.model,
          mirostat_tau: this.modelParameters.mirostat_tau.model,
          repeat_penalty: 1.1,

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
              this.loadingResponse = false
              console.log('Stream complete')
              console.log(this.answer)
              this.parseAnswer(this.answer)
              return;
            }
            let chunkRaw = new TextDecoder().decode(value);
            const chunkArray = chunkRaw.split('data:').slice(1)
            for (let chunk of chunkArray) {
              try {
                chunk = JSON.parse(chunk.split(': ping -')[0])

                this.answer
                  += chunk['choices'][0]['text']
              } catch {
                console.log('il parsing non è andato a buon fine')
              }

            }

            return reader.read().then(processStream);
          };

          reader.read().then(processStream);

        })
        .catch(error => {
          console.error(error);
          this.loadingResponse = false
          return error.body;
        })
        .catch(error => {
          console.log(error)
          this.loadingResponse = false
        });


    },

  },
  mounted() {
    this.prepareExtraction();
  }
}
</script>

<template>
  <q-card class="relative-position q-pa-none shadow-0 overflow-overlay"
          style="height: 90%"
  >
    <div v-if="loadingResponse === true"
         class="absolute-top-left bg-grey-3 row justify-center items-center"
         style="height: 100%; width: 100%; z-index: 10; opacity: 50%">
      <q-spinner-gears
        color="primary"
        size="8em"
      />

    </div>
    <q-card class="full-height column full-width no-wrap">
      <q-tabs class="text-grey"
              v-model="tab"
              dense
              active-color="primary"
              active-bg-color="grey-3"
              indicator-color="primary"
              align="justify"
              narrow-indicator
      >
        <q-tab name="table" label="Table"/>
        <q-tab name="prompt" label="Prompt"/>
        <q-tab name="timeline" label="Timeline"/>
      </q-tabs>
      <q-separator class="bi-border"/>
      <q-tab-panels v-model="tab" animated class="column no-wrap full-height overflow-hidden "
                    style="height: 100%"
                    @transition=" prepareExtraction()"
      >
        <q-tab-panel name="table" class="column full-height q-ma-none">
          <div class="text-h6">Table</div>
          <q-btn
            class="q-ma-sm" color="primary"
            @click="extractMedications()"
          >Extract medications
          </q-btn>
          <q-table
            class="col"
            title="Medications"
            :rows="table.rows"
            :columns="table.columns"
            row-key="name"
            :rows-per-page-options="[0, 10, 20, 30]"
          />
        </q-tab-panel>
        <q-tab-panel class="overflow-hidden full-height q-pa-none" name="prompt"
        >
          <div class="full-height column justify-between full-width no-wrap overflow-auto">
            <q-list class="full-height column no-wrap">
              <q-expansion-item
                icon="settings"
                label="Model Settings"
                header-class=""
              >
                <q-card class="q-pa-none col">
                  <q-card-section class="q-pa-sm flex justify-start">
                    <q-input
                      v-for="param in modelParameters" :key="param"
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

              <q-separator/>

              <q-expansion-item
                icon="edit_note"
                label="Prompt"
                header-class=""
                default-opened>
                <q-card>
                  <div class="bg-grey-3 overflow-scroll column full-height">
                    <div class="col-grow flex q-pa-sm justify-end bg-grey-4 full-height">
                      <div style="display: flex;">
                        <q-btn class="q-mx-sm" round dense flat icon="cleaning_services" @click="clear()"/>
                        <q-btn class="q-mx-sm" round dense flat icon="send" @click="extractMedications()"/>
                      </div>
                    </div>

                    <div class="q-pa-sm col overflow-auto flex column">
                      <p style="margin: 0">
                        {{ this.template.slice(0, this.template.indexOf('{system_message}') - 1) }}</p>
                      <textarea class="bg-white col q-pa-sm no-border rounded-borders full-width"
                                style="resize: none"
                                placeholder="System message"
                                v-model="this.systemMessage"
                      />
                      <p style="margin: 0"
                         v-html="this.template.slice(this.template.indexOf('{system_message}')+16, this.template.indexOf('{prompt}')-1)
                                  .replace('\n', '<br>')"></p>

                      <div class="col-grow">
                        <textarea placeholder="User message"
                                  @input="adjustHeight()"
                                  class="q-pa-sm no-border rounded-borders full-width bg-white"
                                  ref="userMessage"
                                  v-model="this.prompt"
                        ></textarea>
                      </div>

                      <p style="margin: 0"
                         v-html="this.template.slice(this.template.indexOf('{prompt}')+8, this.template.indexOf('{completion_init}')-1)
                                  .replace('\n', '<br>')"
                      ></p>
                      <textarea contenteditable="true" class="bg-white col q-pa-sm no-border rounded-borders full-width"
                                style="resize: none"
                                placeholder="Completion init"
                                v-model="this.completionInit"
                      />
                    </div>
                  </div>

                </q-card>
              </q-expansion-item>


              <q-separator/>

              <q-expansion-item
                icon="output"
                label="Model Output"
              >
                <q-card>
                  <q-card-section style="white-space: pre-line">
                    {{ answer }}
                  </q-card-section>
                </q-card>
              </q-expansion-item>
              <q-separator/>

            </q-list>
          </div>
        </q-tab-panel>




      </q-tab-panels>
    </q-card>

  </q-card>

</template>

<style scoped lang="scss">

::-webkit-scrollbar {
  display: none;
}

</style>
