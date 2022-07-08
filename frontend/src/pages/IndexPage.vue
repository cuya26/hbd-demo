<template>
  <q-page padding class="row items-strech">
    <div class="col-12 column no-wrap">
      <div class="row no-wrap justify-between" style="height: 100%">
        <div class="column no-wrap" style="width: 55%">
          <div class="q-pb-md">
            <div class="row justify-evenly">
              <q-select style="width: 300px" dense outlined v-model="dischargeLetterName" :options="letterNames" label="Choose the input document" />
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
                  v-model="letterDict[dischargeLetterName]"
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
              v-model="modelName"
              :options="modelNames"
              label="Choose a Model"/>
            </div>
          </div>

          <q-card class="" style="height: 590px">
            <q-card-section class="q-pb-none row justify-evenly" >
              <div class="text-h6 text-primary">Model Output</div>
            </q-card-section>
            <q-card-section v-if="modelName==='track1 n2c2 pipeline1'" class="q-pa-md">
              <div class="q-px-md q-pb-md row justify-evenly">
                <q-btn @click="extractValues" rounded color="primary" label="Compute" :disable="dischargeLetterName===null"/>
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
              />
            </q-card-section>
            <q-card-section v-if="modelName==='question answering'" class="q-pa-md">
              <div class="row justify-evenly">
                <q-radio dense v-model="questionType" val="free" label="Free question" />
                <q-radio dense v-model="questionType" val="default" label="Default questions" />
              </div>
              <div v-if="questionType==='default'">
                <div class="q-pb-md"></div>
                  <div class="row justify-evenly"><q-btn rounded @click="answerQuestionList" color="primary" dense style="width: 80px" label="compute"></q-btn></div>
                  <div v-for="element in defaultQuestionsAnswers" :key="element">
                    <div class="q-py-sm text-primary">{{element["question"] + ":"}}</div>
                    <div class="q-px-sm q-py-md text-grey-9"  style="overflow: auto;white-space: pre-line;border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px; height: 45px">
                      <div style="">
                        {{element["answer"]}}
                      </div>
                    </div>
                </div>
              </div>
              <div v-if="questionType==='free'">
                <div class="q-pb-md">
                  <div class="q-py-sm text-primary">Question:</div>
                  <q-input @keyup.enter="answerQuestion()" outlined v-model="question" placeholder="Write a question and press enter"/>
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
      dischargeLetterName: ref(null),
      letterNames: ref([]),
      medicationList: ref([]),
      letterDict: ref({}),
      modelName: ref(null),
      modelNames: ref([
        'track1 n2c2 pipeline1',
        'question answering'
      ]),
      columns,
      loading: ref(false),
      question: ref(null),
      answer: ref(null),
      questionType: ref('default'),
      defaultQuestionsAnswers: ref(
        [
          {question:"Qual è la condizione patologica?", answer: null},
          {question:"Qual è l\'età?", answer: null},
          {question:"Qual è il sesso?", answer: null},
          {question:"Quali farmaci assume attualmente?", answer: null},
          {question:"Quali sono le procedure chirurgiche applicate?", answer: null}
        ]
      )
    }
  },
  methods : {
    extractValues () {
      this.loading=true
      api.post(
        '/extract_data_table',
        { input_text: this.letterDict[this.dischargeLetterName]}
      ).then( (response) => {
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
      api.post(
        '/answer_question',
        {
          input_text: this.letterDict[this.dischargeLetterName],
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
      api.post(
        '/answer_question_list',
        {
          input_text: this.letterDict[this.dischargeLetterName],
          question_answer_list: this.defaultQuestionsAnswers
        },
        { timeout: 120000 },
      ).then( (response) => {
        this.loading=true
        console.log(response.data)
        this.defaultQuestionsAnswers = response.data
      }).catch((error)=>{
        this.loading=false
        console.log('ops an error occurs')
        error.message
      })
    }
  },
  created () {
    api.get(
      '/discharge_letters'
    ).then( (response)=> {
      console.log(response.data)
      this.letterDict = response.data
      this.letterNames = Object.keys(this.letterDict).sort((a, b) => {
        if (a.split('_')[0].length !== b.split('_')[0].length) return b.split('_')[0].length - a.split('_')[0].length
        else return parseInt(a.split('_')[1]) - parseInt(b.split('_')[1])
      })
      // console.log(Object.keys(this.letterDict).sort((a, b) => Number(a.split('_')[1]) < Number(b.split('_')[1])))
      // console.log(['sd_3', 'sd_33', 'sd_11'].sort((a,b)=> parseInt(a.split('_')[1]) - parseInt(b.split('_')[1]) ))
      console.log(this.letterNames)
    })
  }
})
</script>
