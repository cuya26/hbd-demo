<template>
  <q-page padding class="row items-stretch" style="height: 100%">
    <div class="col-12 column no-wrap">
      <div
        ref="resizableBlock"
        class="row no-wrap justify-between"
        style="height: 100%"
      >
        <div
          class="column no-wrap"
          :style="{ width: this.resizableWidth + '%' }"
        >
          <div class="q-pb-md">
            <div style="height: 40px"></div>
          </div>
          <q-card class="items-strech" style="height: 90%">
            <div class="col-12 column no-wrap" style="height: 100%">
              <q-card-section class="row justify-between">
                <div class="col-3"></div>
                <div class="text-h6 text-primary">Input</div>
                <div class="col-3">
                  <div class="col-6 justify-end row">
                    <q-btn
                      v-if="inputMode === 'saliency'"
                      label="text"
                      color="primary"
                      flat
                      rounded
                      dense
                      @click="inputMode = 'edit'"
                    />
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
                    v-if="dropzoneURL !== '' && inputMode !== 'saliency'"
                    rounded
                    unelevated
                    toggle-color="primary"
                    color="white"
                    text-color="primary"
                    :options="[
                      { label: 'PDF', value: 'pdf' },
                      { label: 'REGIONS', value: 'regions' },
                      { label: 'TEXT', value: 'edit' },
                    ]"
                  />
                </div>
              </q-card-section>
              <q-card-section style="height: 90%">
                <div
                  v-if="!loadingSaliencyMap"
                  style="overflow: auto; flex-grow: 1; max-height: 100%"
                >
                  <q-input
                    @drop.prevent="this.dropFunction"
                    @dragover.prevent
                    @dragenter.prevent="highlightColor = true"
                    @dragleave="highlightColor = false"
                    :class="
                      (highlightColor ? 'bg-light-blue-2' : '') + ' text-grey-7'
                    "
                    v-if="inputMode === 'edit'"
                    outlined
                    placeholder="Insert text or drag and drop a pdf of txt file"
                    class="text-grey-7"
                    type="textarea"
                    input-style="min-height: 560px;white-space: nowrap;overflow-x: scroll;font-family: monospace;font-size: small"
                    style=""
                    v-model="inputLetter"
                  />
                  <embed
                    :src="dropzoneURL"
                    style="min-height: 560px; width: 100%"
                    class=""
                    v-if="inputMode === 'pdf'"
                    type="application/pdf"
                  />
                  <embed
                    :src="dropzoneURL2"
                    style="min-height: 560px; width: 100%"
                    class=""
                    v-if="inputMode === 'regions'"
                    type="application/pdf"
                  />
                  <!-- <q-input outlined v-model="text" :dense="dense" /> -->
                  <!-- <div class="text-grey-7" style="white-space: pre-line">{{dischargeLetterName == null ? '' : letterDict[dischargeLetterName]}}</div> -->
                </div>

                <div
                  style="height: 100%"
                  v-if="loadingSaliencyMap"
                  class="row justify-evenly"
                >
                  <div style="height: 100%" class="column justify-evenly">
                    <q-spinner color="primary" size="6em" />
                  </div>
                </div>
                <div
                  v-if="inputMode === 'saliency'"
                  class="text-grey-7"
                  style="overflow: auto; flex-grow: 1; max-height: 100%"
                >
                  <div style="min-height: 490px; white-space: pre-line">
                    <mark
                      style="white-space: pre-line"
                      v-for="element in saliencyMap"
                      :key="element"
                      :class="element.color"
                    >
                      {{ element.text }}
                    </mark>
                  </div>
                </div>
              </q-card-section>
            </div>
          </q-card>
        </div>
        <div
          style="cursor: col-resize; width: 6px"
          @mousedown="startDrag(this.$refs.resizableBlock)"
        ></div>
        <div
          class="column no-wrap full-height"
          :style="{ width: 100 - this.resizableWidth + '%' }"
        >
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
                  <q-item v-if="!scope.opt.group" v-bind="scope.itemProps">
                    <q-item-section>
                      <q-item-label class="q-pl-md">{{
                        scope.opt.label
                      }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item v-if="scope.opt.group">
                    <q-item-section>
                      <q-item-label class="text-bold text-primary">{{
                        scope.opt.group + ":"
                      }}</q-item-label>
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
                @update:model-value="whenChangeSetupModel"
              />
            </div>
          </div>
          <DeidentificationClassic
            style="height: 90%"
            :inputLetter="inputLetter"
            v-if="setupName === 'Classic'"
          />
          <PharmacologicalEventExtraction
            style="height: 90%"
            :inputLetter="inputLetter"
            :modelConfig="modelConfig['Track1 n2c2 Challenge (en)']"
            v-model:inputMode="inputMode"
            v-model:saliencyMap="saliencyMap"
            v-model:loadingSaliencyMap="loadingSaliencyMap"
            v-if="setupName === 'Track1 n2c2 Challenge (en)'"
          />
          <ChatBot
            style="height: 90%"
            :inputLetter="inputLetter"
            v-if="setupName === 'mistral-7b-openorca-q5'"
          />
          <QuestionAnswering
            v-if="taskName === 'question answering' && setupName !== null"
            style="height: 90%"
            :inputLetter="inputLetter"
            :modelConfig="modelConfig[setupName]"
            v-model:inputMode="inputMode"
            v-model:saliencyMap="saliencyMap"
            v-model:loadingSaliencyMap="loadingSaliencyMap"
          />
          <PatientSearch
            v-if="setupName === 'Patient Search Engine'"
            style="height: 90%"
            v-model:inputLetter="inputLetter"
            v-model:inputMode="inputMode"
          />
          <q-card
            class=""
            style="height: 90%"
            v-if="setupName === 'Medical Information Extraction with LLM'"
          >
            <q-card-section class="row justify-between">
              <div class="col-2"></div>
              <div class="text-h6 text-primary">Output</div>
              <div class="col-2"></div>
            </q-card-section>
            <q-card-section class="" style="height: 100%">
              <medical-information-extraction
                :doc="inputLetter"
                ref="medicalInformationExtractionComponent"
              ></medical-information-extraction>
            </q-card-section>
          </q-card>
          <q-card class="" style="height: 90%" v-if="setupName === null">
            <q-card-section class="row justify-between">
              <div class="col-2"></div>
              <div class="text-h6 text-primary">Output</div>
              <div class="col-2"></div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent, ref } from "vue";
import { api } from "boot/axios";
import MedicalInformationExtraction from "components/MedicalInformationExtraction/MedicalInformationExtraction.vue";
import DeidentificationClassic from "components/DeidentificationClassic.vue";
import PharmacologicalEventExtraction from "components/PharmacologicalEventExtraction.vue";
import ChatBot from "components/ChatBot.vue";
import QuestionAnswering from "components/QuestionAnswering.vue";
import PatientSearch from "components/PatientSearch.vue";

export default defineComponent({
  name: "Health Big Data WG1 Demo",
  components: {
    MedicalInformationExtraction,
    DeidentificationClassic,
    PharmacologicalEventExtraction,
    ChatBot,
    QuestionAnswering,
    PatientSearch,
  },
  setup() {
    return {
      resizableWidth: ref(30),
      draggable: false,
      inputMode: ref("edit"),
      dropzoneURL: ref(""),
      dropzoneURL2: ref(""),
      highlightColor: ref(false),
      saliencyMap: ref([]),
      loadingSaliencyMap: ref(false),
      inputLetter: ref(),
      letterNames: ref([]),
      letterDict: ref({}),
      taskName: ref(null),
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
          setupNames: [
            "Track1 n2c2 Challenge (en)",
            "Medical Information Extraction with LLM",
          ],
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
  methods: {
    startDrag() {
      this.draggable = true;
      this.$refs.resizableBlock.addEventListener("mousemove", this.handleDrag);
      this.$refs.resizableBlock.addEventListener("mouseup", this.stopDrag);
    },

    handleDrag(event) {
      if (this.draggable) {
        const draggableWidth =
          event.clientX -
          this.$refs.resizableBlock.getBoundingClientRect().left;
        const blockWidth = this.$refs.resizableBlock.offsetWidth;
        let newResizable1Width = Math.min(
          Math.max((draggableWidth / blockWidth) * 100, 30),
          70
        );
        this.resizableWidth = newResizable1Width.toFixed(2);
      }
    },
    stopDrag() {
      this.draggable = false;
      this.$refs.resizableBlock.removeEventListener(
        "mousemove",
        this.handleDrag
      );
      this.$refs.resizableBlock.removeEventListener("mouseup", this.stopDrag);
    },
    dropFunction(dragEvent) {
      // TODO add revokeObjectURL
      const dropzoneFile = dragEvent.dataTransfer.files[0];
      // TODO add docx
      if (dropzoneFile.type === "application/pdf") {
        this.dropzoneURL = URL.createObjectURL(dropzoneFile);
        this.inputMode = "pdf";
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
            api
              .post("return_pdf", uploadForm, {
                headers: {
                  Accept: "application/pdf",
                },
                responseType: "blob",
              })
              .then((response) => {
                // this.inputMode = 'regions'
                var blob = new Blob([response.data], {
                  type: "application/pdf",
                });
                this.dropzoneURL2 = URL.createObjectURL(blob);
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
    whenChangeSetupModel() {
      if (this.inputMode === "saliency") this.inputMode = "edit";
    },
    updateTaskName() {
      this.setupName = null;
      this.taskName = this.taskName.value;
    },
  },
});
</script>
