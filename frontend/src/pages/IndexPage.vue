<template>
  <q-page padding class="row items-strech">
    <div class="col-12 column no-wrap">
      <div class="row no-wrap justify-between" style="height: 100%">
        <div class="column no-wrap" style="width: 55%">
          <div class="q-pb-md">
            <div class="row justify-evenly">
              <q-select v-if="dischargeLetterLoaded" style="width: 300px" dense outlined v-model="dischargeLetterName" @update:model-value="inputLetter=letterDict[dischargeLetterName]" :options="letterNames" label="Choose the input document" />
              <q-btn
              v-if="!dischargeLetterLoaded"
              style="height: 40px"
              rounded 
              color="primary"
              label="Upload Letters"
              @click="this.$refs.filePicker.$el.click()"
              />
              <q-file
                v-model="upload"
                v-show="false"
                ref="filePicker"
                accept=".json"
                @update:model-value="loadLetters"
              />
            </div>
          </div>
          <q-card class="items-strech" style="height: 590px">
            <div class="col-12 column no-wrap" style="height: 100%">
              <q-card-section class="row justify-evenly">
                <div class="text-h6 text-primary">Input Text</div>
              </q-card-section>
              <q-card-section style="max-height: 90%">
                <div style="overflow: auto; flex-grow: 1;max-height: 100%">
                  <q-input
                  outlined
                  placeholder="Insert text or choose a discharge letter"
                  class="text-grey-7"
                  type="textarea"
                  input-style="min-height: 490px"
                  style="white-space: pre-line;"
                  v-model="inputLetter" 
                  />
                  <!-- <q-input outlined v-model="text" :dense="dense" /> -->
                  <!-- <div class="text-grey-7" style="white-space: pre-line">{{dischargeLetterName == null ? '' : letterDict[dischargeLetterName]}}</div> -->
                </div>
              </q-card-section>
            </div>
          </q-card>
        </div>

        <div class="column no-wrap" style="width: 42%">
          <div class="q-pb-md">
            <div class="row justify-evenly">
              <q-select
              style="width: 300px"
              dense
              outlined
              v-model="taskName"
              :options="taskNames"
              label="Choose a Task"
              @update:model-value="setupName=null"
              />
              <q-select
              style="width: 300px"
              dense
              outlined
              v-model="setupName"
              :options="setupNames[taskName]"
              label="Choose a Model"/>
            </div>
          </div>

          <q-card class="" style="height: 590px">
            <q-card-section class="q-pb-none row justify-evenly" >
              <div class="text-h6 text-primary">Model Output</div>
            </q-card-section>
            <q-card-section v-if="setupNames['pharmacological event extraction'].includes(setupName)" class="q-pa-md">
              <div class="q-px-md q-pb-md row justify-evenly">
                <q-btn @click="extractValues" rounded color="primary" label="Compute" :disable="inputLetter===null"/>
              </div>
              <q-table
                class="my-sticky-virtscroll-table"
                :rows-per-page-options="[0]"
                table-header-style="text-align: left"
                table-header-class="align-left text-primary text-bold"
                wrap-cells
                hide-bottom
                dense
                virtual-scroll
                :virtual-scroll-item-size="48"
                :virtual-scroll-sticky-size-start="48"
                separator="cell"
                :columns="columns"
                :rows="medicationList"
                :loading="loading"
              >
                <template v-slot:loading>
                  <q-inner-loading showing color="primary" />
                </template>
              </q-table>
            </q-card-section>
            <q-card-section
            v-if="setupNames['question answering (extractive)'].includes(setupName) || setupNames['question answering (generative)'].includes(setupName)"
            class="q-pa-md">
              <div class="row justify-evenly">
                <q-radio dense v-model="questionType" val="free" label="Free question" />
                <q-radio dense v-model="questionType" val="default" label="Default questions" />
              </div>
              <div v-if="questionType==='default'">
                <div class="q-pb-md"></div>
                  <div class="row justify-evenly">
                    <q-btn
                    rounded
                    @click="answerQuestionList"
                    color="primary"
                    dense style="width: 80px"
                    label="compute"
                    :disable="inputLetter===null"
                    :loading="loading"/>
                  </div>
                  <div v-for="element in defaultQuestionsAnswers[modelConfig[setupName].lang]" :key="element">
                    <div class="q-py-sm text-primary">{{element["question"] + ":"}}</div>
                    <div class="q-px-sm q-py-md text-grey-9"  style="overflow: auto;white-space: pre-line;border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px; height: 52px">
                      <div style="">
                        {{element["answer"]}}
                      </div>
                    </div>
                </div>
              </div>
              <div v-if="questionType==='free'">
                <div class="q-pb-md">
                  <div class="q-py-sm text-primary">Question:</div>
                  <q-input
                  @keyup.enter="answerQuestion()"
                  outlined
                  v-model="question"
                  :disable="inputLetter===null"
                  placeholder="Write a question and press enter"
                  :loading="loading"/>
                </div>
                <!-- <div class="q-pa-md row justify-evenly">
                  <q-btn rounded color="primary" label="Compute" :disable="dischargeLetterName===null"/>
                </div> -->
                <div>
                  <div class="q-py-sm text-primary">Answer:</div>
                  <div class="q-px-sm q-py-md text-grey-9"  style="overflow: auto;white-space: pre-line;border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px; height: 90px">
                    <div style="">
                      {{answer}}
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<style lang="sass">
.my-sticky-virtscroll-table
  /* height or max-height is important */
  height: 455px

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
import { api } from 'boot/axios'


const columns = [
  { name: 'drug', label: 'Farmaco', field: 'entity', required: true, sortable: true, align: 'left'},
  // { name: 'drug', label: 'Sentence', field: 'sentence', required: true, sortable: true, align: 'left'},
  { name: 'disposition', label: 'Evento', field: 'disposition', required: true, sortable: true, align: 'left' },
  { name: 'action', label: 'Azione', field: 'Action', required: true, sortable: true, align: 'left' },
  { name: 'negation', label: 'Negazione', field: 'Negation', required: true, sortable: true, align: 'left' },
  { name: 'temporality', label: 'Tempo', field: 'Temporality', required: true, sortable: true, align: 'left' },
  { name: 'actor', label: 'Attuatore', field: 'Actor', required: true, sortable: true, align: 'left' },
  { name: 'certainty', label: 'Certezza', field: 'Certainty', required: true, sortable: true, align: 'left' }
]

export default defineComponent({
  name: 'IndexPage',
  setup () {
    return {
      inputLetter: ref(null),
      taskName: ref(null),
      taskNames: ref([
        "pharmacological event extraction",
        "question answering (extractive)",
        "question answering (generative)",
        "anonymisation TODO",
        "patient cohort search TODO"
      ]),
      upload: ref(null),
      dischargeLetterLoaded: ref(false),
      dischargeLetterName: ref(null),
      letterNames: ref([]),
      medicationList: ref([]),
      letterDict: ref({}),
      setupName: ref(null),
      setupNames: ref({
        "pharmacological event extraction" : ['track1 n2c2 pipeline1 (en)'],
        "question answering (extractive)": ['roberta-large (it)'],
        "question answering (generative)": [
          "t5-base (en)",
          "t5-base (it)"
        ],
        "anonymisation TODO": ["We are still working on it"],
        "patient cohort search TODO": ["We are still working on it"]
      }),
      columns,
      loading: ref(false),
      question: ref(null),
      answer: ref(null),
      questionType: ref('default'),
      modelConfig: ref(
        {
          "track1 n2c2 pipeline1 (en)": {modelName: 'track1 n2c2 pipeline1', lang: "en"},
          'roberta-large (it)': {modelName: 'deepset/xlm-roberta-large-squad2', lang:"it"},
          "t5-base (en)": {modelName: "valhalla/t5-base-qa-qg-hl", lang: "en"},
          "t5-base (it)": {modelName: "Narrativa/mT5-base-finetuned-tydiQA-xqa", lang: "it"}

        }
      ),
      defaultQuestionsAnswers: ref(
        {
          it: [
            {question:"Qual è la condizione patologica del paziente?", answer: null},
            {question:"Qual è l\'età del paziente?", answer: null},
            {question:"Qual è il sesso del paziente?", answer: null},
            {question:"Quali farmaci assume attualmente il paziente?", answer: null},
            {question:"Quali sono le procedure chirurgiche applicate al paziente?", answer: null}
          ],
          en: [
            {question:"What is the patient's pathological condition?", answer: null},
            {question:"What is the age of the patient?", answer: null},
            {question:"What is the patient's gender?", answer: null},
            {question:"What medications does the patient currently take?", answer: null},
            {question:"What are the surgical procedures applied to the patient?", answer: null}
          ]
        }
      )
    }
  },
  methods : {
    extractValues () {
      this.loading=true
      api.post(
        '/extract_data_table',
        { input_text: this.inputLetter}
      ).then( (response) => {
        this.loading=false
        console.log(response.data)
        this.medicationList = response.data
      }).catch((error)=>{
        this.loading=false
        console.log('ops an error occurs')
        error.message
      })
    },
    answerQuestion () {
      this.loading=true
      let modelType = null
      if (this.taskName == "question answering (extractive)") modelType = 'extractive'
      else modelType = 'generative'
      api.post(
        '/answer_question',
        {
          model_type: modelType,
          model_name: this.modelConfig[this.setupName].modelName,
          model_lang: this.modelConfig[this.setupName].lang,
          input_text: this.inputLetter,
          question: this.question
        },
      ).then( (response) => {
        this.loading=false
        console.log(response.data)
        this.answer = response.data
      }).catch((error)=>{
        this.loading=false
        console.log('ops an error occurs')
        error.message
      })
    },
    answerQuestionList () {
      this.loading=true
      let modelType = null
      if (this.taskName == "question answering (extractive)") modelType = 'extractive'
      else modelType = 'generative'
      let lang = this.modelConfig[this.setupName].lang
      api.post(
        '/answer_question_list',
        {
          model_type: modelType,
          model_name: this.modelConfig[this.setupName].modelName,
          model_lang: lang,
          input_text: this.inputLetter,
          question_answer_list: this.defaultQuestionsAnswers[lang]
        },
        { timeout: 60000 },
      ).then( (response) => {
        this.loading=false
        console.log(response.data)
        this.defaultQuestionsAnswers[lang] = response.data
      }).catch((error)=>{
        this.loading=false
        console.log('ops an error occurs')
        error.message
      })
    },
    loadLetters (upload) {
      var reader = new FileReader()
      reader.onload = (e) => {
        // console.log(reader.result)
        // console.log(e)
        const sessionJSON = JSON.parse(reader.result)
        // console.log(sessionJSON)
        this.letterDict = sessionJSON
        this.letterNames = Object.keys(this.letterDict).sort((a, b) => {
          if (a.split('_')[0].length !== b.split('_')[0].length) return b.split('_')[0].length - a.split('_')[0].length
          else return parseInt(a.split('_')[1]) - parseInt(b.split('_')[1])
        })
        this.dischargeLetterLoaded = true
      }
      reader.readAsText(upload)
    }
  },
  created () {
    // api.get(
    //   '/discharge_letters'
    // ).then( (response)=> {
    //   console.log(response.data)
    //   this.letterDict = response.data
    //   this.letterNames = Object.keys(this.letterDict).sort((a, b) => {
    //     if (a.split('_')[0].length !== b.split('_')[0].length) return b.split('_')[0].length - a.split('_')[0].length
    //     else return parseInt(a.split('_')[1]) - parseInt(b.split('_')[1])
    //   })
    //   console.log(this.letterNames)
    // })
  }
})
</script>
