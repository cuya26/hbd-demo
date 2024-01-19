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
        brokenOutput: false,
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
        completionInit:`Here the extracted table with the required informations
[CSV_START]
medication || dose || mode || frequency`,
        userMessage: `TASK: Named Entity Medical Extraction
Extract all the medications mentioned in the clinical document and for each of them extracts the corresponding:
- dose: the specified amount of medication taken at one specific time.
- mode: is the way by which a drug, fluid, poison, or other substance is taken into the body. Modes of administration are generally classified by the location at which the substance is applied. Common examples include oral and intravenous administration.
- frequency: is indicated by how many times a day the medication is to be administered or how often it is to be administered in hours or minutes.
Put all the extracted entities into a csv table with the columns medication, dose, mode, and frequency.
Follow this csv format "medication || dose || mode || frequency".
[CLINICAL_DOCUMENT_START]
{file}
[CLINICAL_DOCUMENT_END]`,
        systemMessage: `Emulate a tool for the specified task. Strictly follow the provided instructions to execute the task accurately. Your role is to adhere solely to the given guidelines and perform the designated actions without deviation.`,
      },
      timeline: {
        brokenOutput: false,
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
      console.log('parsing medications answer',   answer)
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


    async fixAnswer(body, answer){
      let fixPrompt = `
      Your task it to perfectly extract the structured data in the following text.
      You need to understand the structure and correct the syntax in case it is broken.

      In the output there will be only the structured data, no text.

      TEXT:
      `
      fixPrompt += answer
      return await this.askLLM({...body, prompt: fixPrompt, stream: true,
        stop: ['<|im_end|>']})
    },


    askLLM(body) {
      return axios.api.post(axios.llamaHost + '/v1/completions', {...body, stream: false}, {
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

    fixTimelineAnswer(body, answer){
      let fixPrompt = `The following text must be printed in json file.
Remove all the text and leave only the json.
Fix the json if it is broken.

<text>
{answer}
</text>`
      fixPrompt = fixPrompt.replace('{answer}', answer)
      console.log('fix timeline answer', fixPrompt)
      return this.askLLM({...body.parameters, prompt: fixPrompt, temperature: 0 })
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
      <q-tab-panels v-model="tab" animated class=""
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
            class="col"
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
<!--              <q-btn-->
<!--                v-if="timeline.brokenOutput"-->
<!--                class="q-ma-sm" color="secondary"-->
<!--                @click="this.timeline.times = this.parseTimelineAnswer(fixTimelineAnswer(this.$refs.timelinePromptComponent.prepareData(), this.timeline.answer))"-->
<!--              >Fix with AI-->
<!--              </q-btn>-->
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


