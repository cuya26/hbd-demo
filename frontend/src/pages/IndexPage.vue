<template>
  <q-page padding class="row items-stretch" style="height: 100%">
    <div class="col-12 column no-wrap">
      <div class="q-pb-md" style="width: 50%">
        <div class="row justify-evenly">
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
              <q-item v-if="!scope.opt.group" v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label class="q-pl-md"
                    >{{ scope.opt.label }}
                  </q-item-label>
                </q-item-section>
              </q-item>
              <q-item v-if="scope.opt.group">
                <q-item-section>
                  <q-item-label class="text-bold text-primary"
                    >{{ scope.opt.group + ":" }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>
          <q-select
            style="width: 48%"
            dense
            outlined
            v-model="setupName"
            :options="
              taskName
                ? taskOptionGroups.filter(
                    (optionTask) => optionTask.value === taskName
                  )[0]['setupNames']
                : []
            "
            label="Choose a Model"
          />
        </div>
      </div>
      <div class="row no-wrap justify-between" style="height: 100%">
        <div class="column no-wrap full-height full-width">
          <resizable-drawer v-if="setupName === 'Classic'">
            <template v-slot:block1>
              <input-document
                v-model:input-letter="inputLetter"
              ></input-document>
            </template>
            <template v-slot:block2>
              <DeidentificationClassic
                style="height: 100%"
                :inputLetter="inputLetter"
              />
            </template>
          </resizable-drawer>
          <resizable-drawer v-if="setupName === 'Track1 n2c2 Challenge (en)'">
            <template v-slot:block1>
              <input-document
                v-model:input-letter="inputLetter"
              ></input-document>
            </template>
            <template v-slot:block2>
              <PharmacologicalEventExtraction
                style="height: 100%"
                :inputLetter="inputLetter"
                :modelConfig="modelConfig['Track1 n2c2 Challenge (en)']"
                v-model:inputMode="inputMode"
                v-model:saliencyMap="saliencyMap"
                v-model:loadingSaliencyMap="loadingSaliencyMap"
              />
            </template>
          </resizable-drawer>

          <resizable-drawer v-if="setupName === 'mistral-7b-openorca-q5'">
            <template v-slot:block1>
              <input-document
                v-model:input-letter="inputLetter"
              ></input-document>
            </template>
            <template v-slot:block2>
              <q-card style="height: 100%">
                <MIEChat :doc="inputLetter" />
              </q-card>
            </template>
          </resizable-drawer>
          <resizable-drawer
            v-if="taskName === 'question answering' && setupName !== null"
          >
            <template v-slot:block1>
              <input-document
                v-model:input-letter="inputLetter"
              ></input-document>
            </template>
            <template v-slot:block2>
              <QuestionAnswering
                style="height: 100%"
                :inputLetter="inputLetter"
                :modelConfig="modelConfig[setupName]"
                v-model:inputMode="inputMode"
                v-model:saliencyMap="saliencyMap"
                v-model:loadingSaliencyMap="loadingSaliencyMap"
              />
            </template>
          </resizable-drawer>

          <resizable-drawer v-if="setupName === 'Patient Search Engine'">
            <template v-slot:block1>
              <input-document
                v-model:input-letter="inputLetter"
              ></input-document>
            </template>
            <template v-slot:block2>
              <PatientSearch
                style="height: 100%"
                v-model:inputLetter="inputLetter"
                v-model:inputMode="inputMode"
              />
            </template>
          </resizable-drawer>

          <resizable-drawer
            v-if="
              taskName === 'Information Extraction' &&
              setupName === 'Medication & Timeline with LLM'
            "
          >
            <template v-slot:block1>
              <input-document
                v-model:input-letter="inputLetter"
              ></input-document>
            </template>
            <template v-slot:block2>
              <medical-information-extraction
                v-model:doc="inputLetter"
                style="height: 100%"
                ref="medicalInformationExtractionComponent"
              ></medical-information-extraction>
            </template>
          </resizable-drawer>

          <resizable-drawer v-if="setupName === null">
            <template v-slot:block1>
              <input-document
                v-model:input-letter="inputLetter"
              ></input-document>
            </template>
            <template v-slot:block2>
              <q-card style="height: 100%">
                <q-card-section class="row justify-between">
                  <div class="col-2"></div>
                  <div class="text-h6 text-primary">Output</div>
                  <div class="col-2"></div>
                </q-card-section>
              </q-card>
            </template>
          </resizable-drawer>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent, ref } from "vue";
import MedicalInformationExtraction from "components/MedicalInformationExtraction/MedicalInformationExtraction.vue";
import DeidentificationClassic from "components/DeidentificationClassic.vue";
import PharmacologicalEventExtraction from "components/PharmacologicalEventExtraction.vue";
import ChatBot from "components/ChatBot.vue";
import QuestionAnswering from "components/QuestionAnswering.vue";
import PatientSearch from "components/PatientSearch.vue";
import MIEChat from "components/MedicalInformationExtraction/MIEChat.vue";
import ResizableDrawer from "src/utils/ResizableDrawer.vue";
import InputDocument from "components/InputDocument.vue";

export default defineComponent({
  name: "Health Big Data WG1 Demo",
  components: {
    InputDocument,
    ResizableDrawer,
    MIEChat,
    MedicalInformationExtraction,
    DeidentificationClassic,
    PharmacologicalEventExtraction,
    QuestionAnswering,
    PatientSearch,
  },

  setup() {
    return {
      modelName: ref(""),
      inputMode: ref("edit"),
      dropzoneURL: ref(""),
      dropzoneURL2: ref(""),
      highlightColor: ref(false),
      saliencyMap: ref([]),
      loadingSaliencyMap: ref(false),
      inputLetter: ref(),
      letterNames: ref([]),
      letterDict: ref({}),
      taskName: ref(""),
      taskNames: ref([
        "deidentification",
        "pharmacological event extraction",
        "question answering (extractive)",
        "question answering (generative)",
        "patient cohort search TODO",
        "Medical Information Extraction",
      ]),
      taskOptionGroups: [
        {
          group: "Privacy",
          disable: true,
        },
        {
          label: "De-Identification",
          value: "deidentification",
          setupNames: [
            // 'regex',
            // 'spaCy (open-source)',
            // 'Stanza (open-source)',
            // 'John Snow Labs (commercial)',
            "Classic",
          ],
        },
        {
          group: "Information Extraction",
          disable: true,
        },
        {
          label: "Table Extraction",
          value: "table extraction",
          setupNames: ["Track1 n2c2 Challenge (en)"],
        },
        {
          label: "Information Extraction",
          value: "Information Extraction",
          setupNames: ["Medication & Timeline with LLM"],
        },
        {
          label: "Question Answering",
          value: "question answering",
          setupNames: [
            // "Translation-based: it->en, t5-base (english)",
            "Extractive: Roberta-large (multilingual)",
            "Generative: t5-base (multilingual)",
            "Extractive: BioBIT Italian",
          ],
        },
        {
          label: "ChatBot",
          value: "ChatBot",
          setupNames: ["mistral-7b-openorca-q5"],
        },
        {
          group: "Search",
          disable: true,
        },
        {
          label: "Patient Cohort Selection",
          value: "patient cohort selection",
          setupNames: ["Patient Search Engine"],
          // setupNames: ['Not ready yet...']
        },
      ],
      setupName: ref(""),
      modelConfig: ref({
        "Track1 n2c2 Challenge (en)": {
          modelName: "track1 n2c2 pipeline1",
          lang: "en",
          modelType: "t5-ner",
          drug: {
            modelName: "simplet5-epoch-6-train-loss-0.2724-val-loss-0.1477",
            lang: "en",
            modelType: "t5-ner",
          },
          disposition: {
            modelName: "Bio_ClinicalBERT_model_trained_disposition-type",
            lang: "en",
            modelType: "bert-dee",
          },
          action: {
            modelName: "Bio_ClinicalBERT_model_trained_Action",
            lang: "en",
            modelType: "bert-dee",
          },
          negation: {
            modelName: "Bio_ClinicalBERT_model_trained_Negation",
            lang: "en",
            modelType: "bert-dee",
          },
          temporality: {
            modelName: "Bio_ClinicalBERT_model_trained_Temporality",
            lang: "en",
            modelType: "bert-dee",
          },
          actor: {
            modelName: "Bio_ClinicalBERT_model_trained_Actor",
            lang: "en",
            modelType: "bert-dee",
          },
          certainty: {
            modelName: "Bio_ClinicalBERT_model_trained_Certainty",
            lang: "en",
            modelType: "bert-dee",
          },
        },
        "Extractive: Roberta-large (multilingual)": {
          modelName: "deepset/xlm-roberta-large-squad2",
          lang: "it",
          modelType: "roberta-qa",
          thresold: 0.0,
        },
        "Extractive: BioBIT Italian": {
          modelName: "data/checkpoints/medBIT-r3-plus_75",
          lang: "it",
          modelType: "roberta-qa",
          thresold: 0.0,
        },
        "Translation-based: it->en, t5-base (english)": {
          modelName: "valhalla/t5-base-qa-qg-hl",
          lang: "en",
          modelType: "t5-qa",
          thresold: 0.6,
        },
        "Generative: t5-base (multilingual)": {
          modelName: "Narrativa/mT5-base-finetuned-tydiQA-xqa",
          lang: "it",
          modelType: "t5-qa",
          thresold: 0.6,
        },
        "mistral-7b-openorca-q5": {
          modelName: "mistral-7b-openorca-q5.ggmlv3.q4_1.bin",
        },
      }),
    };
  },
  mounted() {},
  methods: {
    updateTaskName() {
      this.setupName = null;
      this.taskName = this.taskName.value;
    },
  },
});
</script>
