<script>
import {ref} from "vue";
import {llamaHost} from "boot/axios";
import PromptComponent from "components/MedicalInformationExtraction/Prompt.vue";
/* prettier-ignore */
/* @formatter:off */

/* @formatter:on */
export default {
  name: "MedicationExtraction",
  props: ['doc'],
  emits: ['request-document'],
  components: {PromptComponent},
  watch: {
    doc(newValue, oldValue) {
    }
  },
  data() {
    return {
      medExt: {
        table: ref({
          columns: [
            {name: 'name', label: 'Name', field: 'name', align: 'left', sortable: true},
            {name: 'dose', label: 'Dose', field: 'dose', align: 'left', sortable: true},
            {name: 'frequency', label: 'Frequency', field: 'frequency', align: 'left', sortable: true},
            {name: 'route', label: 'Route', field: 'route', align: 'left', sortable: true},
          ],
          rows: [],
        }),
        answer: `\nAdalat 200 mg p.o. b.i.d. || 200 mg || p.o. || b.i.d.\nZantac 150 mg p.o. b.i.d. || 150 mg || p.o. || b.i.d.\nMagnesium Oxide 40 mg t.i.d. || 40 mg || t.i.d. || nm\nUltram 300 mg q.d. || 300 mg || q.d. || nm\nTrazodone 100 mg q.h.s. || 100 mg || q.h.s. || nm\nAzmacort 80 mg p.r.n. || 80 mg || p.r.n. || nm\naspirin 81 mg q.d. || 81 mg || q.d. || nm\nDyazide 25 mg q.d. || 25 mg || q.d. || nm\nnose spray b.i.d. || nm || nm || nm\ncalcium chloride pills q.d. || nm || nm || nm\nColchicine 600 mg q.d. || 600 mg || q.d. || nm\ncyproheptadine hydrochloride 4 mg b.i.d. q.h.s. || 4 mg || b.i.d. || nm\nanticholesterol med. || nm || nm || nm\nAlbuterol nebulizers 250 mg q.4h. || 250 mg || q.4h. || nm\nAllopurinol 300 mg q.d. || 300 mg || q.d. || nm\nColchicine 0.6 mg q.d. || 0.6 mg || q.d. || nm\ncyproheptadine hydrochloride by mouth 400 mg q.d. || 400 mg || q.d. || nm\nDigoxin 0.125 mg q.d. || 0.125 mg || q.d. || nm\nDiltiazem 30 mg t.i.d. || 30 mg || t.i.d. || nm\nLasix 40 mg p.o. q.d. || 40 mg || p.o. || q.d.\nPercocet 1-2 tablets p.o. q.4h. p.r.n. || 1-2 tablets || p.o. || q.4h. p.r.n.\nDilantin 200 mg p.o. b.i.d. || 200 mg || p.o. || b.i.d.\nTrazodone 100 mg p.o. q.h.s. || 100 mg || p.o. || q.h.s.\n[CSV_1_END]`,
        completionInit: '[CSV_1_START]\n' +
          'medication || dosage || mode || frequency',
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
        times:  [
          {
            "time": "10/17/95",
            "events": ["admission"]
          },
          {
            "time": "none",
            "events": ["This is a 73-year-old man with squamous cell carcinoma of the lung, status post lobectomy and resection of left cervical recurrence, admitted here with fever and neutropenia.", "Recently he had been receiving a combination of outpatient chemotherapy with the CAMP Program.", "Other medical problems include hypothyroidism, hypercholesterolemia, hypertension and neuropathy from Taxol."]
          },
          {
            "time": "none",
            "events": ["He was started on Neupogen, 400 mcg. subq. q.d.", "He was initially treated with antibiotic therapy.", "Chest x-ray showed questionable nodule in the right lower lobe, reasonably stable."]
          },
          {
            "time": "10/19",
            "events": ["WBC rose to 1.7"]
          },
          {
            "time": "none",
            "events": ["The patient had some diarrhea.", "There was no diarrhea on 10/20."]
          },
          {
            "time": "none",
            "events": ["He was feeling well and afebrile.", "The neutropenia resolved"]
          },
          {
            "time": "10/20",
            "events": ["He was discharged home on Neupogen.", "The patient felt to be in satisfactory condition on discharge."]
          }
        ]
        ,
        answer: '',
        completionInit: '',
        userMessage: `
TASK: Temporal Entity Extraction from Medical Document
Extract a coherent chronological sequence of events from the medical document. Use each date mentioned in the text as a timeline delimiter, emphasizing the context for events without specific dates. Ensure that the output is a list of events ordered chronologically, with each event clearly associated with its relative position in the timeline. Be explicit about the importance of maintaining chronological coherence among the events.

The output must be in JSON list of objects where each object contains the "date" key and the  "events" key.
If there is no date (like before admission), put "none"
Example:

[{
 "time": "10/07/1998",
 "headline": "Admission and Diagnosis",
 "events": ["presents with abdominal pain of seven days duration", "admission", "diagnosed with acute pancreatitis"]
}, ... ]

[CLINICAL_DOCUMENT_START]
{file}
[CLINICAL_DOCUMENT_END]
`,
        systemMessage: `Emulate a tool for the specified task. Strictly follow the provided instructions to execute the task accurately. Your role is to adhere solely to the given guidelines and perform the designated actions without deviation.`,
      },

      editaleTable: ref(false),
      answer: ref(`
      \nAdalat 200 mg p.o. b.i.d. || 200 mg || p.o. || b.i.d.\nZantac 150 mg p.o. b.i.d. || 150 mg || p.o. || b.i.d.\nMagnesium Oxide 40 mg t.i.d. || 40 mg || t.i.d. || nm\nUltram 300 mg q.d. || 300 mg || q.d. || nm\nTrazodone 100 mg q.h.s. || 100 mg || q.h.s. || nm\nAzmacort 80 mg p.r.n. || 80 mg || p.r.n. || nm\naspirin 81 mg q.d. || 81 mg || q.d. || nm\nDyazide 25 mg q.d. || 25 mg || q.d. || nm\nnose spray b.i.d. || nm || nm || nm\ncalcium chloride pills q.d. || nm || nm || nm\nColchicine 600 mg q.d. || 600 mg || q.d. || nm\ncyproheptadine hydrochloride 4 mg b.i.d. q.h.s. || 4 mg || b.i.d. || nm\nanticholesterol med. || nm || nm || nm\nAlbuterol nebulizers 250 mg q.4h. || 250 mg || q.4h. || nm\nAllopurinol 300 mg q.d. || 300 mg || q.d. || nm\nColchicine 0.6 mg q.d. || 0.6 mg || q.d. || nm\ncyproheptadine hydrochloride by mouth 400 mg q.d. || 400 mg || q.d. || nm\nDigoxin 0.125 mg q.d. || 0.125 mg || q.d. || nm\nDiltiazem 30 mg t.i.d. || 30 mg || t.i.d. || nm\nLasix 40 mg p.o. q.d. || 40 mg || p.o. || q.d.\nPercocet 1-2 tablets p.o. q.4h. p.r.n. || 1-2 tablets || p.o. || q.4h. p.r.n.\nDilantin 200 mg p.o. b.i.d. || 200 mg || p.o. || b.i.d.\nTrazodone 100 mg p.o. q.h.s. || 100 mg || p.o. || q.h.s.\n[CSV_1_END]`),
      tab: ref('timeline'),
      template: '<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n{completion_init}',

      loadingResponse: ref(false),
      showTemplate: ref(false),
      shrinkPrompt: ref(false),
    }
  },
  methods: {
    adjustHeight() {
      let editableDiv = this.$refs.userMessage;
      if (!editableDiv) return;
      editableDiv.style.height = 0 + 'px';
      editableDiv.style.height = editableDiv.scrollHeight + "px";
    },

    parseMedicationsAnswer(answer) {
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



    fetchModel(body) {
      return fetch(llamaHost + '/v1/completions', {
        method: 'POST',
        body: JSON.stringify(body),
        headers:{
          'Content-Type': 'application/json',
          timeout: 36000
        }
      })
    },

    mapChunk(chunkRaw) {
      chunkRaw = new TextDecoder().decode(chunkRaw);
      const chunkArray = chunkRaw.split('data:').slice(1)
      let res = ''
      for (let chunk of chunkArray) {
        if (chunk.trim() === '[DONE]')
          continue
        try {
          chunk = JSON.parse(chunk.split(': ping -')[0])
          res
            += chunk['choices'][0]['text']
        } catch {
          console.log('il parsing non è andato a buon fine', chunk)
        }
      }
      return res
    },

    processMedicationExtraction(reader, {done, value}) {
      if (done) {
        this.loadingResponse = false
        this.medExt.table.rows = this.parseMedicationsAnswer(this.medExt.answer)
        return;
      }
      let mappedChunk = this.mapChunk(value)
      this.medExt.answer += mappedChunk
      return reader.read().then(this.processMedicationExtraction.bind(null, reader));
    },

    checkNExtractMeds(){
      if(this.medExt.table.rows == this.parseTimelineAnswer(this.medExt.answer)){
        this.extractMedications()
      }
      else{
        this.medExt.table.rows = this.parseMedicationsAnswer(this.medExt.answer)
      }
    },
    async extractMedications(data) {
      this.loadingResponse = true
      this.medExt.answer = ''
      this.fetchModel(
        {
          prompt: data.prompt.replace('{file}', this.doc),
          stream: true,
          stop: ['<|im_end|>'],
          ...data.parameters
        }
      ).then(response => {
        const reader = response.body.getReader();
        return reader.read().then(this.processMedicationExtraction.bind(null, reader));
      })
        .catch(error => {
          console.error(error);
          this.loadingResponse = false
          return error.body;
        })
    },

    checkNExtractTimeline(){
      console.log(JSON.parse(JSON.stringify(this.timeline.times)), JSON.parse(JSON.stringify(this.parseTimelineAnswer(this.timeline.answer))))
      // if(this.timeline.times == this.parseTimelineAnswer(this.timeline.answer)){
        this.extractTimeline()
      //   console.log('same')
      // }
      // else{
      //   this.timeline.times = this.parseTimelineAnswer(this.timeline.answer)
      //   console.log('different')
      // }
    },

    parseTimelineAnswer(answer) {
      let res = []
      try{
        res = JSON.parse(answer)
      }catch (e) {
        console.log('error parsing timeline answer')
        console.log(answer)
        res = [{time: '', events: [], headline: 'Error during extraction'}]
      }
      return res
    },


    processTimelineExtraction(reader, {done, value}) {
      if (done) {
        this.loadingResponse = false
        this.timeline.times = this.parseTimelineAnswer(this.timeline.answer)
        return;
      }
      let mappedChunk = this.mapChunk(value)
      this.timeline.answer += mappedChunk
      return reader.read().then(this.processTimelineExtraction.bind(null, reader));
    },

    async extractTimeline(data) {
      this.loadingResponse = true
      this.timeline.answer = ''
      this.fetchModel(
        {
          prompt: data.prompt.replace('{file}', this.doc),
          stream: true,
          stop: ['<|im_end|>'],
          ...data.parameters
        }
      ).then(response => {
        const reader = response.body.getReader();
        return reader.read().then(this.processTimelineExtraction.bind(null, reader));
      })
        .catch(error => {
          console.error(error);
          this.loadingResponse = false
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
        <q-tab name="timeline" label="Timeline"/>
      </q-tabs>
      <q-separator class="bi-border"/>
      <q-tab-panels v-model="tab" animated class="column no-wrap full-height overflow-hidden "
                    style="height: 100%"
      >
        <q-tab-panel name="table" class="column full-height q-ma-none no-wrap">
          <div class="flex justify-between">
            <div class="text-h6">Table</div>
            <q-toggle
              v-show="medExt.table.rows.length > 0"
              v-model="editaleTable"
              color="primary"
              icon="edit"
              label="Edit table"
            />
          </div>
          <q-btn
            class="q-ma-sm" color="primary"
            @click="checkNExtractMeds()"
          >Extract medications
          </q-btn>
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
                  <q-popup-edit :disable="!editaleTable" v-model="props.row.name" v-slot="scope">
                    <q-input v-model="scope.value" dense autofocus title="Update Name" @keyup.enter="scope.set"/>
                  </q-popup-edit>
                </q-td>
                <q-td key="dose" :props="props">
                  {{ props.row.dose }}
                  <q-popup-edit :disable="!editaleTable" v-model="props.row.dose" v-slot="scope">
                    <q-input v-model="scope.value" dense autofocus title="Update dosage" @keyup.enter="scope.set"/>
                  </q-popup-edit>
                </q-td>
                <q-td key="frequency" :props="props">
                  {{ props.row.frequency }}
                  <q-popup-edit :disable="!editaleTable" v-model="props.row.frequency" v-slot="scope">
                    <q-input v-model="scope.value" dense autofocus title="Update dosage" @keyup.enter="scope.set"/>

                  </q-popup-edit>
                </q-td>
                <q-td key="route" :props="props">
                  {{ props.row.route }}
                  <q-popup-edit :disable="!editaleTable" v-model="props.row.route" v-slot="scope">
                    <q-input v-model="scope.value" dense autofocus title="Update dosage" @keyup.enter="scope.set"/>

                  </q-popup-edit>
                </q-td>
              </q-tr>
            </template>
          </q-table>
          <div>
            <prompt-component
              ref="promptComponent"
              :accordion="true"
              :template="template"
              :answer="medExt.answer"
              :prompt-completion-init="medExt.completionInit"
              :prompt-system-message="medExt.systemMessage"
              :prompt-user-message="medExt.userMessage"
              @askLLM="extractMedications"
              @clear-output="medExt.answer = ''"
            ></prompt-component>
          </div>
        </q-tab-panel>
        <q-tab-panel name="timeline">
          <div class="q-pa-lg">
            <q-btn
              class="q-ma-sm" color="primary"
              @click="checkNExtractTimeline()"
            >Extract timeline
            </q-btn>
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
              ref="promptComponent"
              :template="template"
              :answer="timeline.answer"
              :prompt-completion-init="timeline.completionInit"
              :prompt-system-message="timeline.systemMessage"
              :prompt-user-message="timeline.userMessage"
              @askLLM="extractTimeline"
              @clear-output="timeline.answer = ''"

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
