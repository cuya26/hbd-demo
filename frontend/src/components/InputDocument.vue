<script>
import { ref } from "vue";
import { api } from "boot/axios";

export default {
  name: "InputDocument",
  props: {
    inputLetter: String,
  },
  watch: {
    inputLetter() {
      this.localInputLetter = this.inputLetter;
    },
    localInputLetter() {
      this.$emit("update:inputLetter", this.localInputLetter);
    },
  },

  emits: ["update:inputLetter"],
  data() {
    return {
      inputMode: ref("edit"),
      localInputLetter: "",
      dropzoneURL: ref(""),
      dropzoneURL2: ref(""),
      highlightColor: false,
    };
  },
  methods: {
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
            this.localInputLetter = response.data["pdf_text"];
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
          this.localInputLetter = res.target.result;
        };
        reader.onerror = (err) => console.log(err);
        reader.readAsText(dropzoneFile);
      } else {
        // TODO add error message
        console.log("The dropped file haven't a supported extension");
      }
      this.highlightColor = false;
    },
  },
};
</script>

<template>
  <div class="column no-wrap full-width">
    <q-card class="items-strech" style="height: 100%">
      <div class="col-12 column no-wrap" style="height: 100%">
        <q-card-section class="row justify-between">
          <div class="col-3"></div>
          <div class="text-h6 text-primary">Input</div>
          <div class="col-4">
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
                { label: 'PARTS', value: 'regions' },
                { label: 'TEXT', value: 'edit' },
              ]"
            />
          </div>
        </q-card-section>
        <q-card-section
          style="
            height: 90%;
            width: 95%;
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
          "
        >
          <div style="overflow: auto; flex-grow: 1; height: 100%">
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
              id="pd"
              placeholder="Insert text or drag and drop a pdf of txt file"
              class="text-grey-7 full-height"
              type="textarea"
              input-style="min-height: 560px; height: 100%;overflow-x: scroll;font-family: monospace;font-size: small;"
              style="height: 100%; resize: none"
              v-model="localInputLetter"
            />
            <embed
              :src="dropzoneURL"
              style="min-height: 560px; height: 100%; width: 100%"
              class=""
              v-if="inputMode === 'pdf'"
              type="application/pdf"
            />
            <embed
              :src="dropzoneURL2"
              style="min-height: 560px; height: 100%; width: 100%"
              class=""
              v-if="inputMode === 'regions'"
              type="application/pdf"
            />
            <!-- <q-input outlined v-model="text" :dense="dense" /> -->
            <!-- <div class="text-grey-7" style="white-space: pre-line">{{dischargeLetterName == null ? '' : letterDict[dischargeLetterName]}}</div> -->
          </div>
        </q-card-section>
      </div>
    </q-card>
  </div>
</template>

<style scoped lang="scss"></style>
