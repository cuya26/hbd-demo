<script>
import { ref } from "vue";
import MedicationExtraction from "components/MedicalInformationExtraction/MedicationExtraction.vue";
import TimelineExtraction from "components/MedicalInformationExtraction/TimelineExtraction.vue";
import {
  config,
  saveServer,
} from "components/MedicalInformationExtraction/utils";
import * as docs from "./documents.json";
import Chat from "components/MedicalInformationExtraction/MIEChat.vue";
import ChatBot from "components/ChatBot.vue";
import MIEChat from "components/MedicalInformationExtraction/MIEChat.vue";

let documents = Object.fromEntries(
  Object.entries(docs).filter(([key]) => !key.includes("default"))
);

export default {
  name: "MedicalInformationExtraction",

  components: { MIEChat, TimelineExtraction, MedicationExtraction },
  props: ["doc"],
  emits: ["update:doc"],
  mounted() {},
  data() {
    return {
      docs: documents,
      page: ref("Example Documents"),
      mini: ref(true),
      config: ref(config),
      searchServer: ref(""),
    };
  },
  methods: {
    saveServer,
  },
};
</script>

<template>
  <div class="flex row full-width full-height" style="gap: 5px">
    <q-card class="full-height overflow-auto col column no-wrap">
      <div style="height: 49%; overflow: scroll">
        <medication-extraction
          :doc="doc"
          :show="page === 'Medication Extraction'"
        ></medication-extraction>
      </div>
      <q-separator></q-separator>
      <div style="height: 49%; overflow: scroll">
        <timeline-extraction
          :doc="doc"
          :show="page === 'Timeline Extraction'"
        ></timeline-extraction>
      </div>
    </q-card>
    <q-card class="col-5 full-height overflow-scroll">
      <MIEChat style="height: 100%" :doc="doc" />
    </q-card>
  </div>
</template>

<style scoped lang="scss">
::-webkit-scrollbar {
  display: none;
}
</style>
