<template>
    <q-card>
        <q-card-section class=" row justify-between" >
            <div class="col-2"></div>
            <div class="text-h6 text-primary">Output</div>
            <div class="col-2"></div>
        </q-card-section>
        <q-card-section
        class="q-pa-md" style="height: 85%; overflow:auto"
        >
            <div class="q-py-sm">
            <div class="text-primary">Some default questions (click to load):</div>
            <div v-for="element in defaultQuestionsAnswers[modelConfig.lang]" :key="element">
                <div
                    :style="inputLetter===null?'cursor: not-allowed':'cursor: pointer'"
                    @click="inputLetter===null?null:(question=element['question'],answerQuestion())"
                    class="q-pl-xl q-py-sm text-grey-8 disable"
                >
                    {{'- ' + element["question"]}}
                </div>
            </div>
            </div>
            <div>
            <div class="q-py-sm">
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
                <div class="q-py-sm text-primary">Answers:</div>
                <div v-if="freeQuestionResponse['noAnswer'] == true" class="q-px-sm q-py-md col-12 text-grey-9"  style="overflow: auto;white-space: pre-line;border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px; height: 55px">
                {{"L'informazione non è presente nel testo"}}
                </div>
                <div class="" v-for="(answer, answer_index) in freeQuestionResponse.answers" :key="answer">
                <div v-if="answer.score.toFixed(3) > modelConfig.thresold" class="q-py-sm row justify-between">
                    <div @click="modelConfig.modelType==='t5-qa'?loadSaliencyMapQA(answer.slice_index, answer.text , answer_index, answer.question):null" class="q-px-sm q-py-md col-10 text-grey-9"  style="overflow: auto;white-space: pre-line;border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px; height: 55px">
                    <div style="">
                        {{answer.text}}
                    </div>
                    </div>
                    <div class="q-px-sm q-py-md text-grey-9 row justify-evenly"  style="overflow: auto;white-space: pre-line;border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px; height: 55px; width: 60px">
                        {{(answer.score*100).toFixed() + '%'}}
                    </div>
                </div>
                </div>
                <!-- <div @click="showSaliencyMap=true" class="q-px-sm q-py-md text-grey-9"  style="overflow: auto;white-space: pre-line;border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px; height: 90px">
                <div style="">
                    {{answer}}
                </div>
                </div> -->
            </div>
            </div>
        </q-card-section>
    </q-card>
</template>

<script>
import { defineComponent, ref } from 'vue'
import {api} from "boot/axios";

export default defineComponent({
    name: 'QuestionAnswering',
    props:  [
        'inputLetter',
        'modelConfig',
        'inputMode',
        'saliencyMap',
        'loadingSaliencyMap'
        
    ],
    emits:['update:inputMode', 'update:saliencyMap', 'update:loadingSaliencyMap'],
    data () {
        return {
            defaultQuestionsAnswers: ref(
                {
                it: [
                    {question:"Quale patologia presenta il paziente?", answer: null},
                    {question:"Quali farmaci assume attualmente il paziente?", answer: null},
                    {question:"A quali esami è stato sottoposto il paziente?", answer: null},
                    {question:"Quali sono gli interventi ai quali è stato sottoposto il paziente?", answer: null},
                    {question:"Qual è l'età del paziente?", answer: null}
                ],
                en: [
                    {question:"What pathology does the patient have?", answer: null},
                    {question:"What medication does the patient currently take?", answer: null},
                    {question:"Which diagnostic tests have been performed on the patient?", answer: null},
                    {question:"What interventions have been performed on the patient?", answer: null},
                    {question:"What is the age of the patient?", answer: null}
                ]
                }
            ),
            loading: ref(false),
            question: ref(null),
            freeQuestionResponse: ref({answers: [], noAnswer: false})
        }
    },
    methods : {
        loadSaliencyMapQA (sliceIndex, answer, answer_index, question) {
            this.$emit('update:loadingSaliencyMap', true);
            api.post(
                '/compute_saliency_map',
                {
                task_type: 'qa',
                input_text: this.inputLetter,
                slice_index: sliceIndex,
                answer: answer,
                question: question,
                model_type: this.modelConfig.modelType,
                model_name: this.modelConfig.modelName,
                model_lang: this.modelConfig.lang,
                },
                { timeout: 360000 }
            ).then ( (response) => {
                this.$emit('update:loadingSaliencyMap', false);
                this.$emit('update:inputMode', "saliency");
                console.log(response.data.saliency_map)
                console.log(this.freeQuestionResponse)
                this.$emit('update:saliencyMap', response.data.saliency_map);
            }).catch( (error) =>{
                this.$emit('update:loadingSaliencyMap', false);
                console.log('ops an error occurs during the computing of the saliency maps')
                error.message
            })
        },
        answerQuestion () {
            this.loading=true
            this.$emit('update:inputMode', "edit");
            this.freeQuestionResponse = {answers: [], noAnswer: false}
            api.post(
                '/answer_question',
                {
                model_type: this.modelConfig.modelType,
                model_name: this.modelConfig.modelName,
                model_lang: this.modelConfig.lang,
                // answer_number: this.modelConfig[this.setupName].answerNumber,
                input_text: this.inputLetter,
                question: this.question,
                compute_saliency_map: false,
                },
                { timeout: 360000 },
            ).then( (response) => {
                this.loading=false
                console.log(response.data)
                this.freeQuestionResponse = response.data
                let noAnswer = true
                for (const answer of this.freeQuestionResponse.answers ){
                if (answer.score.toFixed(3) > this.modelConfig.thresold){
                    noAnswer = false
                }
                // if (answer.text !== ''){
                //   noAnswer = false
                // }
                }
                console.log(noAnswer)
                // this.freeQuestionResponse['noAnswer'] = noAnswer
                // if (!noAnswer){
                //   // TODO ordina risposte
                //   this.freeQuestionResponse.answers = this.freeQuestionResponse.answers.slice(0,3)
                // }
            }).catch((error)=>{
                this.loading=false
                console.log('ops an error occurs')
                error.message
            })
        }
    }
})
</script>