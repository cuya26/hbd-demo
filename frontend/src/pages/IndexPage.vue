/* prettier-ignore */
/* @formatter:off */
<template>
  <q-page padding style="height: 100%" class="row items-stretch">
    <div class="col-12 column no-wrap">

      <div class="q-pb-md flex justify-end">
        <div class="row justify-end "
             style="gap: 10px; width: 600px"
        >
          <!-- <q-select
          style="width: 48%"
          dense
          outlined
          v-model="taskName"
          :options="taskNames"
          label="Choose a Task"
          @update:model-value="setupName=null"
          /> -->
          <q-select
            style="width: 48%"
            outlined
            v-model="taskName"
            :options="taskOptionGroups"
            dense
            label="Choose a Task"
            @update:model-value="updateTaskName"
          >
            <template v-slot:option="scope">
              <q-item v-if="!scope.opt.group"
                      v-bind="scope.itemProps"
              >

                <q-item-section>
                  <q-item-label class="q-pl-md">{{ scope.opt.label }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item v-if="scope.opt.group"
              >
                <q-item-section>
                  <q-item-label class="text-bold text-primary">{{ scope.opt.group + ':' }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>
          <q-select
            style="width: 48%"
            dense
            outlined
            v-model="setupName"
            :options="taskName?taskOptionGroups.filter(optionTask => optionTask.value === taskName)[0]['modelNames']:[]"
            label="Choose a Model"
            @update:model-value="whenChangeSetupModel"
          />
        </div>
      </div>
      <div ref="resizableBlock"  class="" style="height: 95%">
        <div class="row no-wrap justify-between" style="height: 90%">
          <div style="max-height: 85%"  class="column no-wrap q-pt-sm" :style="{ width: this.resizableWidth+'%'}">
            <!--<div class="q-pb-md">
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
              <div style="height:40px"></div>
            </div>-->
            <q-card
              class="items-strech col-12 column no-wrap"
              style="height: 100%"
            >
              <div
                class="col-12 column no-wrap"
                style="height: 100%"
              >
                <q-card-section class="row justify-between " >
                  <div class="col-3"></div>
                  <div class="text-h6 text-primary">Input</div>
                  <div class="col-3">
                    <div class="col-6 justify-end row">
                      <q-btn v-if="inputMode==='saliency'" label="text" color="primary" flat rounded dense @click="inputMode='edit'" />
                    </div>
                    <!-- <div class="col-6 justify-end row">
                      <q-btn v-if="inputMode!=='pdf' && dropzoneURL!==''" label="pdf" class="text-primary" flat rounded dense @click="inputMode='pdf'" />
                    </div> -->
                    <q-btn-toggle
                      v-model="inputMode"
                      style="border: 1px solid #027be3"
                      no-caps
                      dense
                      spread
                      v-if='dropzoneURL!=="" && inputMode!=="saliency"'
                      rounded
                      unelevated
                      toggle-color="primary"
                      color="white"
                      text-color="primary"
                      :options="[
                        {label: 'PDF', value: 'pdf'},
                        {label: 'REGIONS', value: 'regions'},
                        {label: 'TEXT', value: 'edit'}
                      ]"
                    />
                  </div>
                </q-card-section>
                <q-card-section class="full-height">
                  <div
                    v-if="!loadingSaliencyMap"
                    style="overflow: auto; flex-grow: 1;height: 100%"
                  >
                    <q-input
                    @drop.prevent="this.dropFunction"
                    @dragover.prevent
                    @dragenter.prevent="highlightColor = true"
                    @dragleave="highlightColor = false"
                    :class="

                      (highlightColor ? 'bg-light-blue-2' : '') +
                      ' text-grey-7'
                    "
                    v-if="inputMode==='edit'"
                    outlined
                    placeholder="Insert text or drag and drop a pdf of txt file"
                    class="text-grey-7 full-height"
                    type="textarea"
                    input-style="min-height: 560px;white-space: nowrap;overflow-x: scroll;font-family: monospace;font-size: small"
                    style=""
                    v-model="inputLetter"
                    />
                    <embed
                      :src="dropzoneURL"
                      style="min-height: 560px;width: 100%"
                      class=""
                      v-if="inputMode==='pdf'"
                      type="application/pdf"
                    />
                    <embed
                      :src="dropzoneURL2"
                      style="min-height: 560px;width: 100%"
                      class=""
                      v-if="inputMode === 'regions'"
                      type="application/pdf"
                    />
                    <!-- <q-input outlined v-model="text" :dense="dense" /> -->
                    <!-- <div class="text-grey-7" style="white-space: pre-line">{{dischargeLetterName == null ? '' : letterDict[dischargeLetterName]}}</div> -->
                  </div>

                  <div style="height: 100%;" v-if="loadingSaliencyMap" class="row justify-evenly">
                    <div style="height: 100%;" class="column justify-evenly">
                      <q-spinner color="primary" size="6em" />
                    </div>
                  </div>
                  <div v-if="inputMode==='saliency'" class="text-grey-7" style="overflow: auto; flex-grow: 1;max-height: 100%">
                    <div style="min-height: 490px; white-space: pre-line">
                    <mark style="white-space: pre-line;" v-for="element in saliencyMap" :key="element" :class="element.color">
                      {{ element.text }}
                    </mark>
                    </div>
                  </div>
                </q-card-section>
              </div>
            </q-card>
          </div>
          <div style="cursor: col-resize; width: 6px"
               @mousedown="startDrag(this.$refs.resizableBlock)"
          >
          </div>
          <div style="max-height: 85%"  class="column no-wrap q-pr-sm q-pt-sm" :style="{ width: 100-this.resizableWidth+'%'}">
  <!--           Model Output Card-->
            <q-card class="" style="height: 100%">
              <q-card-section class=" row justify-between" >
                <div class="col-2"></div>
                <div class="text-h6 text-primary">Output</div>
                  <div class="col-2" v-if="!deidentified"></div>
                  <div v-if="deidentified" class="col-2 justify-end row">
                    <q-btn label="Reset" class="text-primary" flat rounded dense @click="deidentified=false" />
                  </div>
              </q-card-section>
              <!-- pharmacological event extraction Section -->
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
                  :visible-columns="visibleColumns"
                  :rows="medicationList"
                  :loading="loading"
                >
                  <template v-slot:loading>
                    <q-inner-loading showing color="primary" />
                  </template>
                  <template v-slot:body-cell="props">
                    <q-td :props="props">
                        <span style="cursor: pointer" @click="loadSaliencyMapDrugExtraction(props.row.sentence, props.value, props.col.name)">{{ props.value }}</span>
                    </q-td>
                  </template>
                </q-table>
              </q-card-section>
              <q-card-section v-if="setupNames['question answering (extractive)'].includes(setupName) || setupNames['question answering (generative)'].includes(setupName)"
              class="q-pa-md" style="height: 85%; overflow:auto"
              >
                <!-- <div class="row justify-evenly">
                  <q-radio dense v-model="questionType" val="free" label="Free question" />
                  <q-radio dense v-model="questionType" val="default" label="Default questions" />
                </div> -->
                <!-- <div v-if="questionType==='default'">
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
                      <div class="q-py-sm text-primary">{{element["question"] + ":"}}</div> -->
                      <!-- <div
                      class="q-px-sm q-py-sm text-grey-9"
                      style="overflow: visible;white-space: pre-line;border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px; height: fit-content; min-height: 50px;"
                      >
                        <div style="">
                          {{element["answer"]}}
                        </div>
                      </div> -->
                      <!-- <div v-if="freeQuestionResponse['noAnswer'] == true" class="q-px-sm q-py-md col-12 text-grey-9"  style="overflow: auto;white-space: pre-line;border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px; height: 55px">
                        {{"L'informazione non è presente nel testo"}}
                      </div>
                      <div class="q-py-sm" v-for="answer in element.answers" :key="answer">
                        <div v-if="answer.score.toFixed(2) > answerScoreThreshold" class="row justify-between">
                          <div class="q-px-sm q-py-md col-10 text-grey-9"  style="overflow: auto;white-space: pre-line;border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px; height: 55px">
                            <div style="">
                              {{answer.text}}
                            </div>
                          </div>
                          <div class="q-px-sm q-py-md text-grey-9 row justify-evenly"  style="overflow: auto;white-space: pre-line;border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px; height: 55px; width: 60px">
                              {{answer.score.toFixed(2)*100+'%'}}
                          </div>
                        </div>
                      </div>
                  </div>
                </div> -->
                <!-- <q-dialog v-model="showSaliencyMap">
                  <q-card class="column no-wrap" style="min-width: 100%; height: 95%">
                    <q-card-section class="row justify-between">
                      <div class="text-h5">Interpretation</div>
                      <div class="col-1 justify-end row">
                        <q-btn class='' icon="close" flat round dense v-close-popup />
                      </div>
                    </q-card-section>
                    <q-card-section>
                      <div class="" sytle='height:500px'>
                        <mark v-for="element in saliencyMap" :key="element" :class="element.color">
                          {{ element.text }}
                        </mark>
                      </div>
                    </q-card-section>
                  </q-card>
                </q-dialog> -->
                <div class="q-py-sm">
                  <div class="text-primary">Some default questions (click to load):</div>
                  <div v-for="element in defaultQuestionsAnswers[modelConfig[setupName].lang]" :key="element">
                      <div
                        :style="inputLetter===null?'cursor: not-allowed':'cursor: pointer'"
                        @click="inputLetter===null?null:(question=element['question'],answerQuestion())"
                        class="q-pl-xl q-py-sm text-grey-8 disable"
                      >
                        {{'- ' + element["question"]}}
                      </div>
                  </div>
                </div>
                <div v-if="questionType==='free'">
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
                      <div v-if="answer.score.toFixed(3) > modelConfig[setupName].thresold" class="q-py-sm row justify-between">
                        <div @click="loadSaliencyMapQA(answer.slice_index, answer.text , answer_index, answer.question)" class="q-px-sm q-py-md col-10 text-grey-9"  style="overflow: auto;white-space: pre-line;border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px; height: 55px">
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
              <q-card-section v-if="setupNames['deidentification'].includes(setupName)"
              class="" style="height: 90%"
              >
                <div v-if="!deidentified" class="q-pl-sm q-pt-sm column justify-begin no-wrap" style="height:100%">
                  <div class=" q-pb-md row justify-evenly">
                    <q-btn
                    style="width: 100px"
                    dense
                    :disable="inputLetter===null"
                    label="de-identify"
                    rounded
                    :loading="loading"
                    color="primary"
                    @click="deidentify()"
                  />
                  </div>

                  <div class="q-pl-md q-py-md column">
                    <div class="">Select the entities that you want to de-identify:</div>
                    <div class="row justify-start q-pb-sm" v-for="entityType in Object.keys(deidentificationConf[setupName])" :key="entityType">
                      <q-checkbox
                      v-model="deidentificationConf[setupName][entityType].show"
                      style="width: 150px"
                      :color="deidentificationConf[setupName][entityType].color"
                      :label="deidentificationConf[setupName][entityType].name"
                      @update:model-value="value => resetDeidModel(value, entityType)"
                      />

                      <q-select
                      v-if="deidentificationConf[setupName][entityType].show && setupName==='custom'"
                      v-model="deidentificationConf[setupName][entityType].value"
                      :options="deidentificationConf[setupName][entityType].options"
                      dense
                      outlined
                      style="width: 170px"
                      />
                    </div>
                    <!-- <q-checkbox v-model="deidentificationDict['Codice Fiscale']" false-value="" true-value="select model" color="red-6" label="Codice Fiscale" /> -->
                  </div>

                  <div class="q-pl-md" v-if="deidentificationConf[setupName].date?deidentificationConf[setupName]['date'].show:false">
                    <q-select
                    v-model="dateAnonymLevel"
                    :options="optionsDateAnonymLevel"
                    dense
                    outlined
                    label="Select level of date anonymization"
                    style="width: 300px"
                    />
                  </div>
                </div>
                <div v-show="deidentified" ref="deidentifiedTextDiv"  class="q-pa-md q-m" style="white-space: pre-line; max-height: 560px; min-height: 560px ;overflow:auto; border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px;">
                  ""
                </div>
              </q-card-section>
              <q-card-section v-if="setupNames['ChatBot'].includes(setupName)"
              class="" style="height: 90%"
              >
                <div v-if="loadingChatBot" class="column justify-center items-center no-wrap col-12" style="height: 100%">
                    <q-spinner color="primary" size="6em" />
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
              <q-card-section v-if="setupNames['patient cohort selection'].includes(setupName)"
              class="" style="height: 90%"
              >
              <div style="width: 100%;" class="q-pa-sm">
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
                <div class="q-pt-md">
                  <q-table
                    class="my-sticky-virtscroll-table"
                    :rows-per-page-options="[0]"
                    table-header-style="text-align: left"
                    table-header-class="align-left text-primary text-bold"
                    wrap-cells
                    dense
                    separator="cell"
                    :visible-columns="visiblePatientColumns"
                    :columns="patientColumns"
                    :rows="patientResults"
                    :loading="loadingPatientSearch"
                  >
                    <template v-slot:loading>
                      <q-inner-loading showing color="primary" />
                    </template>
                    <template v-slot:body-cell="props">
                      <q-td :props="props">
                          <span style="cursor: pointer" @click="showRetrievedDocument(props.row.text)">{{ props.value }}</span>
                      </q-td>
                    </template>
                  </q-table>
                </div>
              </div>
            </q-card-section>
            <q-card-section
              class="q-pa-none shadow-0" style="height: 100%"
              v-if="setupNames['Medical Information Extraction'].includes(setupName)">
            <medical-information-extraction
              :doc="inputLetter"
              ref="medicalInformationExtractionComponent"
            @request-document="requestDocument"
            ></medical-information-extraction>

            </q-card-section>
            </q-card>
          </div>
      </div>
    </div>
    </div>

  </q-page>
</template>

/* prettier-ignore */
/* @formatter:off */
<style lang="sass">
.my-sticky-virtscroll-table
  /* height or max-height is important */
  height: 500px

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
/* @formatter:on*/

import { defineComponent, ref } from 'vue'
import { api, patientSearchApi, llamaHost } from 'boot/axios'
import MedicalInformationExtraction from "components/MedicalInformationExtraction.vue";


const columns = [
  { name: 'drug', label: 'Farmaco', field: 'entity', required: true, sortable: true, align: 'left'},
  { name: 'sentence', label: 'Sentence', field: 'sentence', required: false, sortable: false, align: 'left'},
  { name: 'disposition', label: 'Evento', field: 'disposition', required: true, sortable: true, align: 'left' },
  { name: 'action', label: 'Azione', field: 'Action', required: true, sortable: true, align: 'left' },
  { name: 'negation', label: 'Negazione', field: 'Negation', required: true, sortable: true, align: 'left' },
  { name: 'temporality', label: 'Tempo', field: 'Temporality', required: true, sortable: true, align: 'left' },
  { name: 'actor', label: 'Attuatore', field: 'Actor', required: true, sortable: true, align: 'left' },
  { name: 'certainty', label: 'Certezza', field: 'Certainty', required: true, sortable: true, align: 'left' }
]

const patientColumns = [
{ name: 'document_id', label: 'id', field: 'document_id', required: true, sortable: false, align: 'left'},
{ name: 'context', label: 'context', field: 'context', required: true, sortable: false, align: 'left'},
{ name: 'text', label: 'text', field: 'text', required: false, sortable: false, align: 'left'}
]

const visiblePatientColumns = [
  'document_id',
  'context'
]


const visibleColumns = [
'drug',
'disposition',
'action',
'negation',
'temporality',
'actor',
'certainty',
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
};

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
  assistente: [
    { content: "Ciao sono il tuo Assistente come posso aiutarti?", role: "assistant" }
  ],
  practitioner: [
    { content: "Hi, I'm the Practitioner how can I help you?", role: "assistant" }
  ],
  deidentification: [
    { content: "Ciao sono il tuo assistente Vicuna come posso aiutarti?", role: "assistant" },
    { content: 'Perpiacere sostituisci tutte le informazioni seguenti con il termine "[redatto]": Sostituisci qualsiasi stringa che possa essere un nome o un acronimo o le iniziali, i nomi dei pazienti, i nomi dei medici, i nomi dei dottori o delle dottoresse, elimina i nomi dei cercapersone, i nomi del personale medico, elimina qualsiasi stringa che possa essere una località o un indirizzo, come "3970 Longview Drive", elimina qualsiasi stringa che assomigli a "qualcosa di anni" o "età 37", elimina le date e gli ID e le date di registrazione, eliminare i nomi delle cliniche e degli ospedali, elimina le professioni come "manager" ed elimina i contatti personali:', role: "user" },
    { content: "Ti darò un esempio perpiacere anonimizzalo", role: "user"},
    { content: "Certo, riportami pure il testo che vuoi anonimizzare", role: "assistant"}
  ],
  deidentificationEng: [
    { content: "Hi, I'm Vicuna an assistant how can I help you?", role: "assistant" },
    { content: 'Please anonymize the following clinical note.Replace all the following information with the term “[redacted]”: Redact any strings that might be aname or acronym or initials, patients’ names, doctors’ names, the names of the M.D.or Dr.,redact any pager names, medical staff names, redact any strings that might be a location or address, such as “3970 Longview Drive”, redact any strings that look like “something years old” or “age 37”,redact any dates and IDs and record dates, redact clinic and hospital names, redact professions such as “manager”, redact any contact information:', role: "user" },
    { content: "I will give you a sample, please anonymize it", role: "user"},
    { content: "Sure, please provide the sentence you would like me to anonymize.", role: "assistant"}
  ]
}

export default defineComponent({
  name: 'IndexPage',
  components: {MedicalInformationExtraction},
  setup () {
    return {
      resizableWidth: ref(30),
      draggable: false,
      visiblePatientColumns,
      patientColumns,
      patientResults: ref([]),
      patientSearchText: ref(''),
      loadingPatientSearch: ref(false),
      attached: ref(false),
      attachedDocument: ref(''),
      chatPrompts,
      initChatHistory,
      loadingChatBot: ref(false),
      loadingChatResponse: ref(false),
      inputText: ref(""),
      chatConfig,
      chatHistory: ref(initChatHistory['default']),
      inputMode: ref("edit"),
      dropzoneURL: ref(""),
      dropzoneURL2: ref(""),
      text: ref(""),
      highlightColor: ref(false),
      visibleColumns,
      loadingSaliencyMap: ref(false),
      deidentified: ref(false),
      dateAnonymLevel: ref('hide date'),
      optionsDateAnonymLevel: ref([
        'hide date',
        'Keep only the year',
        'keep only month'
      ]),
      dictDateAnonymLevel: ref({
        'hide date': 'hide',
        'Keep only the year': 'year',
        'keep only month': 'month'
      }),
      // Person Name, Fiscal Code, Email, Telephone, Address, Zip Code, Age, Organisation, Date
      deidentificationConf: ref({
        'regex': {
          'fiscal_code': {
            show: true,
            color: 'red-4',
            options: [
                'regex'
              ],
            value: 'regex',
            default: 'regex',
            name: ' Fiscal Code'
          },
          'email': {
            show: true,
            color: 'indigo-5',
          options: [
              'regex'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Email'
          },
          'telephone': {
            show: true,
            color: 'yellow-5',
          options: [
              'regex'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Telephone'

          },
          'zipcode': {
            show: true,
            color: 'brown-5',
            options: [
                'regex'
              ],
            value: 'regex',
            default: 'regex',
            name: 'Zip Code'
          },
          'date': {
            show: true,
            color: 'green-5',
          options: [
              'regex'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Date'
          },
          'age': {
            show: true,
            color: 'purple-5',
          options: [
              'john', 'regex'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Age'
          },
        },
        'spaCy (open-source)': {
          'person': {
            show: true,
            color: 'pink-5',
            options: [
              'john', 'spacy', 'stanza'
            ],
            value: 'spacy',
            default: 'stanza',
            name: 'Person Name'
          },
          'address': {
            show: true,
            color: 'orange-5',
          options: [
              'john', 'spacy', 'stanza'
            ],
            value: 'spacy',
            default: 'stanza',
            name: 'Address'
          },
          'organization': {
            show: true,
            color: 'teal-5',
          options: [
              'john', 'spacy', 'stanza'
            ],
            value: 'spacy',
            default: 'stanza',
            name: 'Organization',
          },
        },
         'Stanza (open-source)': {
          'person': {
            show: true,
            color: 'pink-5',
            options: [
              'john', 'spacy', 'stanza'
            ],
            value: 'stanza',
            default: 'stanza',
            name: 'Person Name'
          },
          'address': {
            show: true,
            color: 'orange-5',
          options: [
              'john', 'spacy', 'stanza'
            ],
            value: 'stanza',
            default: 'stanza',
            name: 'Address'
          },
          'organization': {
            show: true,
            color: 'teal-5',
          options: [
              'john', 'spacy', 'stanza'
            ],
            value: 'stanza',
            default: 'stanza',
            name: 'Organization',
          }
        },
        'custom': {
          'person': {
            show: true,
            color: 'pink-5',
            options: [
              'spacy', 'stanza'
            ],
            value: 'stanza',
            default: 'stanza',
            name: 'Person Name'
          },
          'fiscal_code': {
            show: true,
            color: 'red-4',
          options: [
              'regex'
            ],
            value: 'regex',
            default: 'regex',
            name: ' Fiscal Code'
          },
          'email': {
            show: true,
            color: 'indigo-5',
          options: [
              'regex'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Email'
          },
          'telephone': {
            show: true,
            color: 'yellow-5',
          options: [
              'regex'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Telephone'
          },
          'address': {
            show: true,
            color: 'orange-5',
          options: [
              'spacy', 'stanza'
            ],
            value: 'stanza',
            default: 'stanza',
            name: 'Address'
          },
           'zipcode': {
            show: true,
            color: 'brown-5',
          options: [
              'regex'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Zip Code'
          },
          'age': {
            show: true,
            color: 'purple-5',
          options: [
              'regex'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Age'
          },
          'organization': {
            show: true,
            color: 'teal-5',
          options: [
              'spacy', 'stanza'
            ],
            value: 'stanza',
            default: 'stanza',
            name: 'Organization',
          },
          'date': {
            show: true,
            color: 'green-5',
          options: [
              'regex'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Date'
          },
        },
      })
      ,
      deidentificationDict: ref({
        'regex' : {
          'telephone': "regex",
          'date': "regex",
          'email': "regex",
          'zipcode': "regex",
          'fiscal_code': "regex"
        },
        'spaCy (open-source)': {
          'person': "spacy",
          'organization': "spacy",
          'address': "spacy"
        },
        'Stanza (open-source)': {
          'person': "spacy",
          'organization': "spacy",
          'address': "spacy"
        },
        // 'John Snow Labs (commercial)': {
        //   'person': "john",
        //   'organization': "john",
        //   'telephone': "john",
        //   'age': "john",
        //   'zipcode': "john",
        //   'address': "john",
        //   'fiscal_code': "john"
        // },
        'custom': {
          'person': "john",
          'organization': "john",
          'telephone': "john",
          'date': "regex",
          'age': "john",
          'email': "regex",
          'zipcode': "regex",
          'address': "john",
          'fiscal_code': "regex"
        }
      }),
      deidentifiedText: ref(''),
      // editMode: ref(true),
      showSaliencyMap: ref(false),
      saliencyMap: ref([]),
      inputLetter: ref(null),
      taskName: ref(null),
      taskNames: ref([
        "deidentification",
        "pharmacological event extraction",
        "question answering (extractive)",
        "question answering (generative)",
        "patient cohort search TODO",
        "Medical Information Extraction"
      ]),
      // Add hierarchy to the Tasks:
      // - Privacy
      // -- De-identifcation
      // - Information Extraction
      // -- Pharmaceutical Event Extraction
      // -- Question Answering
      // - Search
      // -- Patient Cohort Selection (TODO)
      taskOptionGroups: [
        {
          group: 'Privacy',
          disable: true
        },
        {
          label: 'De-Identification',
          value: 'deidentification',
          modelNames: [
            'regex',
            'spaCy (open-source)',
            'Stanza (open-source)',
            // 'John Snow Labs (commercial)',
            'custom'
          ]
        },
        {
          group: 'Information Extraction',
          disable: true
        },
        {
          label: 'Pharmaceutical Event Extraction',
          value: 'pharmacological event extraction',
          modelNames: ['Track1 n2c2 Challenge (en)']
          // modelNames: ['Not ready yet...']
        },
        {
          label: 'Medical Information Extraction',
          value: 'Medical Information Extraction',
          modelNames: ["Mistral"]
        },
        {
          label: 'Question Answering',
          value: 'question answering',
          modelNames: [
          // "Translation-based: it->en, t5-base (english)",
          'Extractive: Roberta-large (multilingual)',
          "Generative: t5-base (multilingual)",
          "Extractive: BioBIT Italian"
        ],
        },
        {
          label: 'ChatBot',
          value: 'ChatBot',
          modelNames: [
            "mistral-7b-openorca-q5",
            // "gpt4-x-vicuna-13B",
            // "vic13b-uncensored",
            // "medalpaca-13b"
          ]
        },
        {
          group: 'Search',
          disable: true
        },
        {
          label: 'Patient Cohort Selection',
          value: 'patient cohort selection',
          modelNames: ["Patient Search Engine"]
          // modelNames: ['Not ready yet...']
        }

      ],
      upload: ref(null),
      dischargeLetterLoaded: ref(false),
      dischargeLetterName: ref(null),
      letterNames: ref([]),
      medicationList: ref([]),
      letterDict: ref({}),
      setupName: ref(null),
      setupNames: ref({
        "pharmacological event extraction" : ['Track1 n2c2 Challenge (en)'],
        "question answering (extractive)": [
          'Extractive: Roberta-large (multilingual)',
          "Extractive: BioBIT Italian"
        ],
        "question answering (generative)": [
          "Translation-based: it->en, t5-base (english)",
          "Generative: t5-base (multilingual)"
        ],
        "deidentification": [
          'regex',
          'spaCy (open-source)',
          'Stanza (open-source)',
          'custom'
        ],
        "patient cohort selection": ["Patient Search Engine"],
        "ChatBot": [
          "mistral-7b-openorca-q5",
          "gpt4-x-vicuna-13B",
          "vic13b-uncensored",
          "medalpaca-13b"
        ],
        "Medical Information Extraction": ["Mistral"]
      }),
      columns,
      loading: ref(false),
      question: ref(null),
      freeQuestionResponse: ref({answers: [], noAnswer: false}),
      answerScoreThreshold: ref({
        'generative': 0.5,
        'extractive': 0.0
      }),
      questionType: ref('free'),
      modelConfig: ref(
        {
          'Track1 n2c2 Challenge (en)': {
            modelName: 'track1 n2c2 pipeline1',
            lang: "en",
            modelType: 't5-ner',
            'drug': {
              modelName: 'simplet5-epoch-6-train-loss-0.2724-val-loss-0.1477',
              lang: "en",
              modelType: 't5-ner'
            },
            'disposition': {
              modelName: 'Bio_ClinicalBERT_model_trained_disposition-type',
              lang: 'en',
              modelType: 'bert-dee'
            },
            'action': {
              modelName: 'Bio_ClinicalBERT_model_trained_Action',
              lang: 'en',
              modelType: 'bert-dee'
            },
            'negation': {
              modelName: 'Bio_ClinicalBERT_model_trained_Negation',
              lang: 'en',
              modelType: 'bert-dee'
            },
            'temporality': {
              modelName: 'Bio_ClinicalBERT_model_trained_Temporality',
              lang: 'en',
              modelType: 'bert-dee'
            },
            'actor': {
              modelName: 'Bio_ClinicalBERT_model_trained_Actor',
              lang: 'en',
              modelType: 'bert-dee'
            },
            'certainty': {
              modelName: 'Bio_ClinicalBERT_model_trained_Certainty',
              lang: 'en',
              modelType: 'bert-dee'
            }
          },
          'Extractive: Roberta-large (multilingual)': {
            modelName: 'deepset/xlm-roberta-large-squad2',
            lang:"it",
            modelType: 'roberta-qa',
            thresold: 0.0
          },
          "Extractive: BioBIT Italian": {
            modelName: 'data/checkpoints/medBIT-r3-plus_75',
            lang: 'it',
            modelType: 'roberta-qa',
            thresold: 0.0
          },
          "Translation-based: it->en, t5-base (english)": {
            modelName: "valhalla/t5-base-qa-qg-hl",
            lang: "en",
            modelType: 't5-qa',
            thresold: 0.6
          },
          "Generative: t5-base (multilingual)": {
            modelName: "Narrativa/mT5-base-finetuned-tydiQA-xqa",
            lang: "it",
            modelType: 't5-qa',
            thresold: 0.6
          },
          "mistral-7b-openorca-q5": {
            modelName: "mistral-7b-openorca-q5.ggmlv3.q4_1.bin"
          },
          "gpt4-x-vicuna-13B": {
            modelName: "gpt4-x-vicuna-13B.ggmlv3.q5_1.bin",
          },
          "vic13b-uncensored": {
            modelName: "ggml-vic13b-uncensored-q4_1.bin"
          },
          "medalpaca-13b": {
            modelName: "medalpaca-13B.ggmlv3.q4_0.bin"
          }

        }
      ),
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
      )
    }
  },
  methods : {
    startDrag() {
      this.draggable = true;
      this.$refs.resizableBlock.addEventListener("mousemove", this.handleDrag);
      this.$refs.resizableBlock.addEventListener("mouseup", this.stopDrag);
    },

    handleDrag(event) {
      if (this.draggable) {
        const draggableWidth = event.clientX - this.$refs.resizableBlock.getBoundingClientRect().left;
        const blockWidth = this.$refs.resizableBlock.offsetWidth;
        let newResizable1Width = Math.min(Math.max((draggableWidth / blockWidth) * 100, 30), 70)
        this.resizableWidth = newResizable1Width.toFixed(2);
      }
    },
    stopDrag() {
      this.draggable = false;
      this.$refs.resizableBlock.removeEventListener("mousemove", this.handleDrag);
      this.$refs.resizableBlock.removeEventListener("mouseup", this.stopDrag);
    },
    loadSaliencyMapQA (sliceIndex, answer, answer_index, question) {
      this.loadingSaliencyMap = true
      api.post(
        '/compute_saliency_map',
        {
          task_type: 'qa',
          input_text: this.inputLetter,
          slice_index: sliceIndex,
          answer: answer,
          question: question,
          model_type: this.modelConfig[this.setupName].modelType,
          model_name: this.modelConfig[this.setupName].modelName,
          model_lang: this.modelConfig[this.setupName].lang,
        },
        { timeout: 360000 }
      ).then ( (response) => {
        this.loadingSaliencyMap = false
        this.inputMode="saliency"
        console.log(response.data.saliency_map)
        console.log(this.freeQuestionResponse)
        this.saliencyMap = response.data.saliency_map
      }).catch( (error) =>{
        this.loadingSaliencyMap = false
        console.log('ops an error occurs during the computing of the saliency maps')
        error.message
      })
    },
    loadSaliencyMapDrugExtraction (sentence, target, colName) {

      this.loadingSaliencyMap = true
      api.post(
        '/compute_saliency_map',
        {
          task_type: 'drug_event_extraction',
          task: colName,
          input_text: this.inputLetter,
          sentence: sentence,
          target_text: target,
          model_type: this.modelConfig[this.setupName][colName].modelType,
          model_name: this.modelConfig[this.setupName][colName].modelName,
          model_lang: this.modelConfig[this.setupName][colName].lang,
        },
        { timeout: 360000 }
      ).then ( (response) => {
        this.loadingSaliencyMap = false
        this.inputMode="saliency"
        this.saliencyMap = response.data.saliency_map
      }).catch( (error) =>{
        this.loadingSaliencyMap = false
        console.log('ops an error occurs during the computing of the saliency maps')
        error.message
      })
    },
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
      this.inputMode="edit"
      this.freeQuestionResponse = {answers: [], noAnswer: false}
      api.post(
        '/answer_question',
        {
          model_type: this.modelConfig[this.setupName].modelType,
          model_name: this.modelConfig[this.setupName].modelName,
          model_lang: this.modelConfig[this.setupName].lang,
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
          if (answer.score.toFixed(3) > this.modelConfig[this.setupName].thresold){
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
    },
    answerQuestionList () {
      this.loading=true
      his.inputMode="edit"
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
          question_answer_list: this.defaultQuestionsAnswers[lang],
          compute_saliency_map: false
        },
        { timeout: 360000 },
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
    deidentify () {
      this.loading = true

      let deidentificationModelDict = {}
      for ( const [entityType, entityTypeDict] of Object.entries(this.deidentificationConf['custom'])) {
        if ( this.deidentificationConf[this.setupName][entityType] ) {
          deidentificationModelDict[entityType] = this.deidentificationConf[this.setupName][entityType].value
        } else {
          deidentificationModelDict[entityType] = ''
        }
      }
      console.log(deidentificationModelDict)
      api.post(
        '/deidentify',
        {
        cfg: {
          models: deidentificationModelDict,
          mask: {
            mode: "tag",
            special_character: "*",
            date_level: this.dictDateAnonymLevel[this.dateAnonymLevel]
          }
        },
        input_text: this.inputLetter
      }).then( (response) => {
        let deidentifiedText = response.data['deidentified_text']
        this.$refs.deidentifiedTextDiv.innerHTML = this.highlight(deidentifiedText)
        // this.deidentifiedText = this.deidentifiedText.replace(/<DATA>/, '<span class="bg-primary"><DATA></span>')
        this.deidentified = true
        this.loading = false
      }).catch( (error) => {
        this.loading=false
        console.log('ops an error occurs')
        error.message
      })
    },
    highlight (text) {

      text = text.replace(/</g, '&lt').replace(/>/g, '&gt')

      text = text.replace(/&ltTELEFONO&gt/g, '<span class="bg-yellow-3">&ltTELEFONO&gt</span>')
      text = text.replace(/&ltCAP&gt/g, '<span class="bg-brown-3">&ltCAP&gt</span>')
      text = text.replace(/&ltE-MAIL&gt/g, '<span class="bg-indigo-3">&ltE-MAIL&gt</span>')
      text = text.replace(/&ltPERSONA&gt/g, '<span class="bg-pink-3">&ltPERSONA&gt</span>')
      text = text.replace(/&ltORGANIZZAZIONE&gt/g, '<span class="bg-teal-3">&ltORGANIZZAZIONE&gt</span>')
      text = text.replace(/&ltINDIRIZZO&gt/g, '<span class="bg-orange-3">&ltINDIRIZZO&gt</span>')
      text = text.replace(/&ltDATA&gt/g, '<span class="bg-green-3">&ltDATA&gt</span>')
      text = text.replace(/&ltCF&gt/g, '<span class="bg-red-4">&ltCF&gt</span>')
      text = text.replace(/&ltETÀ&gt/g, '<span class="bg-purple-4">&ltETÀ&gt</span>')

      // this.$refs.deidentifiedTextDiv.$el
      // this.$refs.deidentifiedTextDiv.replace(/prova/, '<span>prova</span>')
      // this.$refs.deidentifiedTextDiv.innerHTML = this.$refs.deidentifiedTextDiv.innerHTML.replace(/<DATA>/, '<span>####</span>')
      return text
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
    },
    whenChangeSetupModel () {
      // Load the chatbot model
      if ( this.taskName.includes('ChatBot') ){
        this.loadChatBot()
      }
      // reset answer question ansqwering model
      if ( this.taskName.includes('question') ){
        this.freeQuestionResponse = {answers: [], noAnswer: false}
        for ( const lang of Object.keys(this.defaultQuestionsAnswers) ) {
          for ( const index of Object.keys(this.defaultQuestionsAnswers[lang]) )
            this.defaultQuestionsAnswers[lang][index]["answer"] = null
            this.question = null
        }
      }
      // reset
      this.deidentified = false
    },
    resetDeidModel(value, entityType) {
      if (value === true ) this.deidentificationConf[this.setupName][entityType].value = this.deidentificationConf[this.setupName][entityType].default
      if (value === false) this.deidentificationConf[this.setupName][entityType].value = ''
    },
    updateTaskName () {
      this.setupName = null
      this.taskName = this.taskName.value
    },
    dropFunction(dragEvent) {
      // TODO add revokeObjectURL
      const dropzoneFile = dragEvent.dataTransfer.files[0];
      // TODO add docx
      if (dropzoneFile.type === "application/pdf") {
        this.dropzoneURL = URL.createObjectURL(dropzoneFile);
        this.inputMode = 'pdf'
        // console.log(dropzoneFile);
        // console.log(dragEvent.dataTransfer);
        // console.log(this.dropzoneURL);
        const uploadForm = new FormData();
        uploadForm.append("uploaded_pdf", dropzoneFile);
        // uploadForm.append("notes", "this are my notes");
        api
          .post("convert_pdf", uploadForm, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          })
          .then((response) => {
            this.inputLetter = response.data["pdf_text"];
            api.post("return_pdf", uploadForm, {
              headers: {
                "Accept": "application/pdf",
              },
              responseType: 'blob'
            })
              .then((response) => {
                // this.inputMode = 'regions'
                  var blob = new Blob([response.data], {
                    type: 'application/pdf'
                  });
                  this.dropzoneURL2 = URL.createObjectURL(blob)
              })
              .catch((error) => {
                console.log(error.message);
              });
          })
          .catch((error) => {
            console.log(error.message);
          });
      } else if (dropzoneFile.type === "text/plain") {
        const reader = new FileReader();
        reader.onload = (res) => {
          this.inputLetter = res.target.result;
        };
        reader.onerror = (err) => console.log(err);
        reader.readAsText(dropzoneFile);
      } else {
        // TODO add error message
        console.log("The dropped file haven't a supported extension");
      }
      this.highlightColor = false;
    },
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
      api.post('/llama_tokenizer', {chat: this.chatPrompts['assistente'].concat(this.chatHistory).concat(currentChat)}
      ).then( (response) => {
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
      })

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
      this.chatHistory = JSON.parse(JSON.stringify(this.initChatHistory['assistente']))
    },
    attachDocument () {
      if (this.inputLetter != null && this.inputLetter != '')
      api.post('/llama_tokenizer_filter', { text: this.inputLetter, max_length: 5500}).then( (response) => {
        this.attachedDocument = response.data.text
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
      }).catch (error => {
        error.message
        console.log('errore caricamento allegato')
      })
    },
    searchPatient () {
      this.loadingPatientSearch = true
      patientSearchApi.post(
        '/patient_search',
        { query: this.patientSearchText}
      ).then( (response) => {
        console.log(response.data)
        this.loadingPatientSearch = false
        this.patientResults = response.data.output
      }).catch( (error) => {
        error.message
        console.log('error with patient search call')
        this.loadingPatientSearch = false
      })
    },
    showRetrievedDocument (text) {
      this.showSaliencyMap = false
      this.inputLetter = text
      this.inputMode = 'edit'
      this.dropzoneURL = ''
    },
    requestDocument(callback){
      callback(this.inputLetter)
    },
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
