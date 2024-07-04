<template>
  <q-page padding class="row items-strech">
    <div class="col-12 column no-wrap" >
      <div class="row no-wrap justify-between" style="height: 100%">

        <div class="column no-wrap" style="width: 40%">
          <div class="q-pb-md">
            <div style="height:40px"></div>
          </div>
          <q-card
            class="items-strech"
            style="height: 680px"
          >
            <div
              class="col-12 column no-wrap"
              style="height: 100%"
            >
              <q-card-section class="row justify-between">
                <div class="col-3"></div>
                <div class="text-h6 text-primary">Source Document</div>
                <div class="col-3">
                  <div class="col-6 justify-end row">
                    <q-btn v-if="inputMode==='saliency'" label="text" color="primary" flat rounded dense @click="inputMode='edit'" />
                  </div>
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
              <q-card-section style="height: 90%">
                <div
                  v-if="!loadingSaliencyMap"
                  style="overflow: auto; flex-grow: 1;max-height: 100%"
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
                  class="text-grey-7"
                  type="textarea"
                  input-style="min-height: 560px;overflow-x: scroll;font-family: monospace;font-size: small"
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
                    style="min-height: 560;width: 100%"
                    class=""
                    v-if="inputMode === 'regions'"
                    type="application/pdf"
                  />
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
        <div class="column no-wrap" style="width: 58%"> 
          <div class="q-pb-md">
            <div class="row justify-evenly">
              <q-select
                outlined
                v-model="taskName"
                :options="taskOptionGroups"
                dense
                label="Choose a Task"
                @update:model-value="updateTaskName"
                style="width: 38%"
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
              style="width: 55%"
              dense
              outlined
              v-model="setupName"
              :options="taskName?taskOptionGroups.filter(optionTask => optionTask.value === taskName)[0]['setupNames']:[]"
              label="Choose a Model"
              @update:model-value="whenChangeSetupModel"
              />
            </div>
          </div>
          <ChatBot
            style="height: 300px"
            :inputLetter="inputLetter"
            :inputMode="inputMode" 
            v-if="setupName === 'mistral-7b-openorca-q5'"
            @update:inputLetter="inputLetter = $event" 
            @update:inputMode="inputMode = $event" 
          />
          <!-- v-model:inputLetter="inputLetter"
            v-model:inputMode="inputMode" -->
          <q-card class="" style="height: 680px" v-if="setupName===null">
            <q-card-section class=" row justify-between" >
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
import { defineComponent, ref } from 'vue'
import { api } from 'boot/axios'
import ChatBot from 'components/ChatBot.vue';
// import PatientSearch from 'components/PatientSearch.vue';


export default defineComponent({
  name: 'Health Big Data WG1 Demo',
  components: {
    ChatBot,
    // PatientSearch
  },
  setup () {
    return {
      inputMode: ref("edit"),
      dropzoneURL: ref(""),
      dropzoneURL2: ref(""),
      highlightColor: ref(false),
      saliencyMap: ref([]),
      loadingSaliencyMap: ref(false),
      inputLetter: ref(null),
      letterNames: ref([]),
      letterDict: ref({}),
      taskName: ref(null),
      taskNames: ref([
        "deidentification",
        "pharmacological event extraction",
        "question answering (extractive)",
        "question answering (generative)",
        "patient cohort search TODO",
        "Medical Information Extraction"
      ]),
      taskOptionGroups: [
        {
          label: 'Patient Search',
          value: 'Patient Search',
          setupNames: [
            "mistral-7b-openorca-q5",
          ]
        },
        // {
        //   group: 'Search',
        //   disable: true
        // },
        // {
        //   label: 'Patient Cohort Selection',
        //   value: 'patient cohort selection',
        //   setupNames: ["Patient Search Engine"]
        //   // setupNames: ['Not ready yet...']
        // }
      ],
      setupName: ref(null),
    }
  },
  methods : {
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
    whenChangeSetupModel () {
      if (this.inputMode === 'saliency') this.inputMode = 'edit'
    },
    updateTaskName () {
      this.setupName = null
      this.taskName = this.taskName.value
    },
  }
})
</script>
