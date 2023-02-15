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
          <q-card class="items-strech" style="height: 680px">
            <div class="col-12 column no-wrap" style="height: 100%">
              <q-card-section class="row justify-between">
                <div class="col-3"></div>
                <div class="text-h6 text-primary">Input Text</div>
                <div class="col-3">
                  <div class="col-6 justify-end row">
                    <q-btn v-if="inputMode==='saliency'" label="editor" color="primary" flat rounded dense @click="inputMode='edit'" />
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
                      {label: 'EDITOR', value: 'edit'}
                    ]"
                  />
                </div>
              </q-card-section>
              <q-card-section style="height: 90%">
                <div v-if="!loadingSaliencyMap" style="overflow: auto; flex-grow: 1;max-height: 100%">
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
                  class="text-grey-7"
                  type="textarea"
                  input-style="min-height: 560px"
                  style="white-space: pre-line;"
                  v-model="inputLetter" 
                  />
                  <embed
                    :src="dropzoneURL"
                    style="min-height: 560px;width: 100%"
                    class=""
                    v-if="inputMode==='pdf'"
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

        <div class="column no-wrap" style="width: 42%">
          <div class="q-pb-md">
            <div class="row justify-evenly">
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
                outlined
                v-model="taskName"
                :options="taskOptionGroups"
                dense
                label="Choose a Task"
                @update:model-value="updateTaskName"
                style="width: 48%"
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

          <!-- Model Output Card -->
          <q-card class="" style="height: 680px">
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
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

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
import { defineComponent, ref } from 'vue'
import { api } from 'boot/axios'


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

const visibleColumns = [
'drug',
'disposition',
'action',
'negation',
'temporality',
'actor',
'certainty',
]

export default defineComponent({
  name: 'IndexPage',
  setup () {
    return {
      inputMode: ref("edit"),
      dropzoneURL: ref(""),
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
                'regex', 'john'
              ],
            value: 'regex',
            default: 'regex',
            name: ' Fiscal Code'
          },
          'email': {
            show: true,
            color: 'indigo-5',
          options: [
              'regex', 'john'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Email'
          },
          'telephone': {
            show: true,
            color: 'yellow-5',
          options: [
              'regex', 'john'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Telephone'

          },
          'zipcode': {
            show: true,
            color: 'brown-5',
            options: [
                'regex', 'john'
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
        'John Snow Labs (commercial)': {
          'person': {
            show: true,
            color: 'pink-5',
            options: [
              'john', 'spacy', 'stanza'
            ],
            value: 'john',
            default: 'stanza',
            name: 'Person Name'
          },
          'fiscal_code': {
            show: true,
            color: 'red-4',
          options: [
              'regex', 'john'
            ],
            value: 'john',
            default: 'regex',
            name: ' Fiscal Code'
          },
          'telephone': {
            show: true,
            color: 'yellow-5',
          options: [
              'regex', 'john'
            ],
            value: 'john',
            default: 'regex',
            name: 'Telephone'

          },
          'address': {
            show: true,
            color: 'orange-5',
          options: [
              'john', 'spacy', 'stanza'
            ],
            value: 'john',
            default: 'stanza',
            name: 'Address'
          },
          'zipcode': {
            show: true,
            color: 'brown-5',
          options: [
              'regex', 'john'
            ],
            value: 'john',
            default: 'regex',
            name: 'Zip Code'
          },
          'age': {
            show: true,
            color: 'purple-5',
          options: [
              'john'
            ],
            value: 'john',
            default: 'john',
            name: 'Age'
          },
          'organization': {
            show: true,
            color: 'teal-5',
          options: [
              'john', 'spacy', 'stanza'
            ],
            value: 'john',
            default: 'stanza',
            name: 'Organization',
          },
        },
        'custom': {
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
          'fiscal_code': {
            show: true,
            color: 'red-4',
          options: [
              'regex', 'john'
            ],
            value: 'regex',
            default: 'regex',
            name: ' Fiscal Code'
          },
          'email': {
            show: true,
            color: 'indigo-5',
          options: [
              'regex', 'john'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Email'
          },
          'telephone': {
            show: true,
            color: 'yellow-5',
          options: [
              'regex', 'john'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Telephone'
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
           'zipcode': {
            show: true,
            color: 'brown-5',
          options: [
              'regex', 'john'
            ],
            value: 'regex',
            default: 'regex',
            name: 'Zip Code'
          },
          'age': {
            show: true,
            color: 'purple-5',
          options: [
              'john'
            ],
            value: 'john',
            default: 'john',
            name: 'Age'
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
        'John Snow Labs (commercial)': {
          'person': "john",
          'organization': "john",
          'telephone': "john",
          'age': "john",
          'zipcode': "john",
          'address': "john",
          'fiscal_code': "john"
        },
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
        "patient cohort search TODO"
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
            'John Snow Labs (commercial)',
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
        },
        {
          label: 'Question Answering',
          value: 'question answering',
          modelNames: [
          "Translation-based: it->en, t5-base (english)",
          'Extractive: Roberta-large (multilingual)',
          "Generative: t5-base (multilingual)",
          "Extractive: BioBIT Italian"
        ],
        },
        {
          group: 'Search',
          disable: true
        },
        {
          label: 'Patient Cohort Selection (TODO)',
          value: 'patient cohort search TODO',
          modelNames: ["We are still working on it"]
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
          'John Snow Labs (commercial)',
          'custom'
        ],
        "patient cohort search TODO": ["We are still working on it"]
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
            modelName: 'data/checkpoints/medBIT-r3-plus_ft_QA',
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
