<script>
import {ref} from "vue";
import * as axios from "boot/axios";
import PromptComponent from "components/MedicalInformationExtraction/Prompt.vue";
/* prettier-ignore */
/* @formatter:off */

/* @formatter:on */
export default {
  name: "MedicationExtraction",
  props: ['doc'],
  components: {PromptComponent},
  watch: {
    doc(newValue, oldValue) {
    }
  },
  data() {
    return {
      medExt: {
        fixPrompt: `<|im_start|>system
Emulate a tool for the specified task. Strictly follow the provided instructions to execute the task accurately. Your role is to adhere solely to the given guidelines and perform the designated actions without deviation.<|im_end|>
<|im_start|>user
The text lying between <text> and </text> tags was supposed to be a JSON array of objects.
The parser failed to parse it.
Your task it to generate a perfect json file from the given text.
Remove any extra text apart from the given JSON array.
The JSON may be malformed. If so, fix it.
Do not print any other text apart from the JSON array.

<text>
{text}
</text>
<|im_end|>
<!im_start|>assistant`,
        brokenOutput: true,
        loading: ref(false),
        table: {
          columns: [
            {name: 'name', label: 'Name', field: 'name', align: 'left', sortable: true},
            {name: 'dose', label: 'Dose', field: 'dose', align: 'left', sortable: true},
            {name: 'frequency', label: 'Frequency', field: 'frequency', align: 'left', sortable: true},
            {name: 'route', label: 'Route', field: 'route', align: 'left', sortable: true},
          ],
          rows: ref([]),
        },
        answer: ``,
        completionInit: `Here the extracted table with the required informations
[CSV_START]
medication || dose || mode || frequency`,
        userMessage: `TASK: Named Entity Medical Extraction
Extract all and only the medication, dosage, mode, frequency from the text.
Put all the extracted entities into a csv table with the columns medication and dosage.
If no data in any of the columns write "nm".
Follow a csv format, like this "medication || dosage || mode || frequency".

[CLINICAL_DOCUMENT_START]
{file}
[CLINICAL_DOCUMENT_END]`,
        systemMessage: `Emulate a tool for the specified task. Strictly follow the provided instructions to execute the task accurately. Your role is to adhere solely to the given guidelines and perform the designated actions without deviation.`,
      },
      timeline: {
        fixAnswer: {
          prompt: `<|im_start|>system
Emulate a tool for the specified task. Strictly follow the provided instructions to execute the task accurately. Your role is to adhere solely to the given guidelines and perform the designated actions without deviation.<|im_end|>
<|im_start|>user
The text lying between <text> and </text> tags was supposed to be a JSON array of objects.
The parser failed to parse it.
Your task it to generate a perfect json file from the given text.
Remove any extra text apart from the given JSON array.
The JSON may be malformed. If so, fix it.
Do not print any other text apart from the JSON array.

<text>
{text}
</text>
<|im_end|>
<!im_start|>assistant`,
          fixPromptDialog: ref(false),
          promptUserMessage: '',
          completionInit: '',
          promptSystemMessage: '',
          settings: {
            max_tokems: 2048,
            mirostat_tau: 3.0,
            temperature: 0,
          }
        },

        brokenOutput: true,
        loading: ref(false),
        times: [{}]
        ,
        answer: '',
        completionInit: '',
        userMessage: `TASK: Temporal Entity Extraction from Medical Document
Extract a coherent chronological sequence of events from the medical document. Use each date mentioned in the text as a timeline delimiter, emphasizing the context for events without specific dates. Ensure that the output is a list of events ordered chronologically, with each event clearly associated with its relative position in the timeline. Be explicit about the importance of maintaining chronological coherence among the events.

The output must be in JSON list of objects where each object contains the "date", "headline" and "events" keys.
If there is no date (for example the event happens before admission), put "none" as date value
Example:

[{
 "time": "10/07/1998",
 "headline": "Admission and Diagnosis",
 "events": ["presents with abdominal pain of seven days duration", "admission", "diagnosed with acute pancreatitis"]
}, ... ]

Generate the JSON array for the following document.
[CLINICAL_DOCUMENT_START]
{file}
[CLINICAL_DOCUMENT_END]

`,
        systemMessage: `Emulate a tool for the specified task. Strictly follow the provided instructions to execute the task accurately. Your role is to adhere solely to the given guidelines and perform the designated actions without deviation.`,
      },

      editableTable: ref(false),
      tab: ref('timeline'),
      template: '<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n{completion_init}',
      showTemplate: ref(false),
      shrinkPrompt: ref(false),
    }
  },
  methods: {


    parseMedicationsAnswer(answer) {
      console.log('parsing medications answer', answer)
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
      return table
    },


    askLLM(body) {
      return axios.api.post(axios.llamaHost + '/v1/completions',
        {
          ...body, stream: false,
          stop: ['<|im_end|>']
        }, {
          'Content-Type': 'application/json',
          timeout: 600000
        }
      )
    },


    checkNExtractMeds() {
      let str1 = JSON.stringify(this.medExt.table.rows)
      let str2 = JSON.stringify(this.parseMedicationsAnswer(this.medExt.answer))
      if (str1 === str2) {
        this.extractMedications(this.$refs.medExtPromptComponent.prepareData())
      } else {
        this.medExt.table.rows = this.parseMedicationsAnswer(this.medExt.answer)
      }
    },


    async extractMedications(data) {
      this.medExt.loading = true
      this.medExt.answer = ''
      this.askLLM(
        {
          prompt: data.prompt.replace('{file}', this.doc),
          stream: true,
          stop: ["<|im_end|>"],
          ...data.parameters
        }
      ).then(response => {
        this.medExt.loading = false
        let answer = response.data.choices[0].text

        this.medExt.answer = answer
        this.medExt.table.rows = this.parseMedicationsAnswer(answer)
      })
        .catch(error => {
          console.error(error);
          this.medExt.loading = false
          return error.body;
        })
    },

    checkNExtractTimeline() {
      let str1 = JSON.stringify(this.timeline.times)
      let str2 = JSON.stringify(this.parseTimelineAnswer(this.timeline.answer))
      if (str1 === str2) {
        this.extractTimeline(this.$refs.timelinePromptComponent.prepareData())
      } else {
        this.timeline.times = this.parseTimelineAnswer(this.timeline.answer)
      }
    },

    async fixTimelineAnswer() {
      let brokenAnswer = this.timeline.answer
      let fixPrompt = this.timeline.fixAnswer.prompt.replace('{text}', brokenAnswer)

      console.log('fix timeline answer', fixPrompt)
      this.timeline.loading = true
      let answer = await this.askLLM({prompt: fixPrompt, max_tokens: 2048, temperature: 0.0, mirostat_tau: 3.0})
      answer = answer.data.choices[0].text
      this.timeline.loading = false
      this.timeline.times = this.parseTimelineAnswer(answer)
      this.timeline.answer = answer
    },

    async fixMedExtAnswer() {
      let brokenAnswer = this.medExt.answer
      let fixPrompt = this.medExt.fixPrompt.replace('{text}', brokenAnswer)

      console.log('fix timeline answer', fixPrompt)
      this.timeline.loading = true
      let answer = await this.askLLM({prompt: fixPrompt, max_tokens: 2048, temperature: 0.0, mirostat_tau: 3.0})
      answer = answer.data.choices[0].text
      this.timeline.loading = false
      this.timeline.times = this.parseTimelineAnswer(answer)
      this.timeline.answer = answer
    },

    parseTimelineAnswer(answer) {
      let res = []
      this.timeline.brokenOutput = false

      try {
        res = JSON.parse(answer)
      } catch (e) {
        console.log('error parsing timeline answer')
        this.timeline.brokenOutput = true
        res = [{}]
      }

      return res
    },

    async extractTimeline(data) {
      this.timeline.loading = true
      this.timeline.answer = ''
      this.askLLM(
        {
          prompt: data.prompt.replace('{file}', this.doc),
          stream: true,
          stop: ['<|im_end|>'],
          ...data.parameters
        }
      ).then(response => {
        let answer = response.data.choices[0].text
        this.timeline.loading = false
        this.timeline.answer = answer
        this.timeline.times = this.parseTimelineAnswer(answer)
      })
        .catch(error => {
          console.error(error);
          this.timeline.loading = false
          return error.body;
        })
    },

  },
}
</script>

<template>
  <q-card class="relative-position q-pa-none shadow-0 overflow-overlay"
          style="height: 90%"
  >

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
        <q-tab name="timeline" label="Timeline"/>
      </q-tabs>
      <q-separator class="bi-border"/>
      <q-tab-panels v-model="tab" animated class="column no-wrap full-height overflow-hidden "
                    style="height: 100%"
      >
        <q-tab-panel name="table" class="column full-height q-ma-none no-wrap">
          <div v-if="medExt.loading === true"
               class="absolute-top-left bg-grey-3 row justify-center items-center"
               style="height: 100%; width: 100%; z-index: 10; opacity: 50%">
            <q-spinner-gears
              color="primary"
              size="8em"
            />

          </div>
          <div class="flex justify-between">


            <q-btn
              class="q-ma-sm" color="primary"
              @click="checkNExtractMeds()"
            >Extract medications
            </q-btn>
            <q-toggle
              v-show="medExt.table.rows.length > 0"
              v-model="editableTable"
              color="primary"
              icon="edit"
              label="Edit table"
            />
          </div>
          <q-table
            class="col col-grow"
            title="Medications"
            :rows="medExt.table.rows"
            :columns="medExt.table.columns"
            row-key="name"
            :rows-per-page-options="[0, 10, 20, 30]"
          >
            <template v-slot:body="props">
              <q-tr :props="props">
                <q-td key="name" :props="props">
                  {{ props.row.name }}
                  <q-popup-edit :disable="!editableTable" v-model="props.row.name" v-slot="scope">
                    <q-input v-model="scope.value" dense autofocus title="Update Name" @keyup.enter="scope.set"/>
                  </q-popup-edit>
                </q-td>
                <q-td key="dose" :props="props">
                  {{ props.row.dose }}
                  <q-popup-edit :disable="!editableTable" v-model="props.row.dose" v-slot="scope">
                    <q-input v-model="scope.value" dense autofocus title="Update dosage" @keyup.enter="scope.set"/>
                  </q-popup-edit>
                </q-td>
                <q-td key="frequency" :props="props">
                  {{ props.row.frequency }}
                  <q-popup-edit :disable="!editableTable" v-model="props.row.frequency" v-slot="scope">
                    <q-input v-model="scope.value" dense autofocus title="Update dosage" @keyup.enter="scope.set"/>

                  </q-popup-edit>
                </q-td>
                <q-td key="route" :props="props">
                  {{ props.row.route }}
                  <q-popup-edit :disable="!editableTable" v-model="props.row.route" v-slot="scope">
                    <q-input v-model="scope.value" dense autofocus title="Update dosage" @keyup.enter="scope.set"/>

                  </q-popup-edit>
                </q-td>
              </q-tr>
            </template>
          </q-table>
          <div>
            <prompt-component
              ref="medExtPromptComponent"
              :accordion="true"
              :template="template"
              :answer="medExt.answer"
              :prompt-completion-init="medExt.completionInit"
              :prompt-system-message="medExt.systemMessage"
              :prompt-user-message="medExt.userMessage"
              @askLLM="extractMedications"
              @clear-output="medExt.answer = ''"
              @answer-changed="medExt.answer = $event"
            ></prompt-component>
          </div>
        </q-tab-panel>
        <q-tab-panel name="timeline">
          <div v-if="timeline.loading === true"
               class="absolute-top-left bg-grey-3 row justify-center items-center"
               style="height: 100%; width: 100%; z-index: 10; opacity: 50%">
            <q-spinner-gears
              color="primary"
              size="8em"
            />

          </div>
          <div class="q-pa-lg">
            <div>
              <q-btn
                class="q-ma-sm" color="primary"
                @click="checkNExtractTimeline()"
              >Extract timeline
              </q-btn>
              <q-btn-dropdown
                split
                v-if="timeline.brokenOutput"
                class="q-ma-sm" color="secondary"
                @click="fixTimelineAnswer()"
                label="Fix with AI"
              >
                <q-list>
                  <q-item clickable v-close-popup @click="timeline.fixAnswer.fixPromptDialog = true">
                    <q-item-section>
                      <q-item-label>Edit fix prompt</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
              <q-dialog v-model="timeline.fixAnswer.fixPromptDialog" persistent>
                <q-card>
                  <q-card-section class="row items-center">
                    <span class="q-ml-sm">You are currently not connected to any network.</span>
                  </q-card-section>
                  <q-card-section>
                    <prompt-component
                      :template="template"
                      :prompt-user-message="timeline.fixAnswer.promptUserMessage"
                      :prompt-completion-init="timeline.fixAnswer.prompt"
                      :prompt-system-message="timeline.fixAnswer.promptSystemMessage"
                    >
                    </prompt-component>
                  </q-card-section>

                  <!-- Notice v-close-popup -->
                  <q-card-actions align="right">
                    <q-btn flat label="Cancel" color="primary" v-close-popup/>
                    <q-btn flat label="Save" color="primary" v-close-popup/>
                  </q-card-actions>
                </q-card>
              </q-dialog>
            </div>

            <q-timeline layout="comfortable" side="right" color="secondary">
              <q-timeline-entry heading>Timeline</q-timeline-entry>

              <q-timeline-entry v-for="time in timeline.times" :key="time"
                                :subtitle="time.time"
                                :title="time.headline"
              >

                <ul>
                  <li v-for="event in time.events" :key="event">
                    {{ event }}
                  </li>
                </ul>

              </q-timeline-entry>

            </q-timeline>
          </div>
          <div>
            <prompt-component
              ref="timelinePromptComponent"
              :template="template"
              :answer="timeline.answer"
              :prompt-completion-init="timeline.completionInit"
              :prompt-system-message="timeline.systemMessage"
              :prompt-user-message="timeline.userMessage"
              @askLLM="extractTimeline"
              @clear-output="timeline.answer = ''"
              @answer-changed="timeline.answer = $event"


            ></prompt-component>
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


