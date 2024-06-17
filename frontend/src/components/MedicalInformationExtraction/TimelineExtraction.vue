<script>
import { ref } from "vue";
import ModelInterface from "./ModelInterface.vue";
import {
  getProperties,
  isAdvanced,
} from "components/MedicalInformationExtraction/utils";
import ISLTimeline from "components/MedicalInformationExtraction/ISLTimeline.vue";
import { useQuasar } from "quasar";

export default {
  name: "TimelineExtraction",
  components: { ModelInterface },
  props: { doc: String, show: Boolean },
  watch: {
    show: function (val) {
      this.$nextTick(() => {});
    },
  },

  mounted() {
    getProperties(this.timeline.taskName).then((response) => {
      this.timelineSettings = JSON.parse(response.data);
    });
  },
  data() {
    return {
      $q: useQuasar(),
      tasks: [],
      template: ref(""),
      timelineSettings: ref({}),
      mapPrompt: ref([
        (s) => {
          let file = this.doc.split("\n");
          for (let i = 0; i < file.length; i++) {
            file[i] = ("" + i).padStart(4, " ") + "| " + file[i];
          }
          file = file.join("\n");
          return s.replace("{file}", file);
        },
      ]),
      showSettings: ref(false),
      timeline: {
        taskName: "ISLTimelineItaThree",
        timelineProp: ref({}),
        timelineFixProp: ref({}),
        fixAnswer: {
          fixPromptDialog: ref(false),
        },

        brokenOutput: false,
        loading: ref(false),
        times: [],
        answer: "",
      },
    };
  },
  methods: {
    isAdvanced,
    checkNExtractTimeline() {
      let str1 = JSON.stringify(this.timeline.times);
      let str2 = JSON.stringify(this.parseTimelineAnswer(this.timeline.answer));
      if (str1 === str2) {
        this.extractTimeline();
      } else {
        this.timeline.times = this.parseTimelineAnswer(this.timeline.answer);
      }
    },

    parseTimelineAnswer(answer) {
      const startIndex = answer.indexOf("[");
      const endIndex = answer.lastIndexOf("]");
      if (startIndex === -1 || endIndex === -1) {
        return [];
      }
      answer = answer.slice(startIndex, endIndex + 1);

      let res = [];
      this.timeline.brokenOutput = false;
      try {
        res = JSON.parse(answer);
      } catch (e) {
        console.log("error parsing timeline answer");
        this.timeline.brokenOutput = true;
        res = [];
      }
      return res;
    },

    openInformationSourceLocalization() {
      this.$q
        .dialog({
          component: ISLTimeline,
          fullWidth: true,
          fullHeight: true,
          // props forwarded to your custom component
          componentProps: {
            timeline: this.timeline.times,
            text: this.doc,
            // ...more..props...
          },
        })
        .onOk(() => {
          console.log("OK");
        })
        .onCancel(() => {
          console.log("Cancel");
        })
        .onDismiss(() => {
          console.log("Called on OK or Cancel");
        });
    },
  },
};
</script>

<template>
  <div>
    <div
      v-show="!showSettings"
      id="child"
      class="full-height q-pa-md column justify-between full-width no-wrap"
    >
      <div
        class="column no-wrap full-height overflow-hidden"
        style="height: 100%"
      >
        <div class="flex full-width justify-between">
          <h6 style="margin: 0">Timeline</h6>
          <q-icon name="settings" @click="showSettings = true" />
        </div>
        <div
          v-if="timeline.loading === true"
          class="absolute-top-left bg-grey-3 row justify-center items-center"
          style="height: 100%; width: 100%; z-index: 10; opacity: 50%"
        >
          <q-spinner-gears color="primary" size="8em" />
        </div>

        <q-timeline dense layout="comfortable" side="right" color="secondary">
          <q-timeline-entry v-if="timeline.times.length === 0">
          </q-timeline-entry>
          <q-timeline-entry
            v-for="time in timeline.times"
            :key="time"
            :subtitle="time.dateValue"
            :title="time.headline"
          >
            <ul>
              {{
                time.description
              }}
            </ul>
          </q-timeline-entry>
        </q-timeline>
        <div class="q-pa-lg">
          <div class="flex justify-between">
            <div class="flex justify-between">
              <div class="flex items-center" style="gap: 0.8em">
                <q-btn
                  class="q-ma-sm"
                  color="primary"
                  @click="this.$refs.timelinePromptComponent.sendLLM()"
                  >Extract timeline
                </q-btn>
                <q-btn
                  v-if="timeline.times.length > 0"
                  @click="this.openInformationSourceLocalization"
                  >See source localization
                </q-btn>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-show="showSettings" class="q-pa-md">
      <div class="flex full-width justify-between">
        <h6 style="margin: 0">Timeline Extraction Settings</h6>
        <q-icon name="close" @click="showSettings = false" />
      </div>
      <model-interface
        ref="timelinePromptComponent"
        v-model:settings="timelineSettings"
        v-model:answer="timeline.answer"
        @loading="timeline.loading = $event"
        @update:answer="
          this.timeline.times = this.parseTimelineAnswer(this.timeline.answer)
        "
        :map-prompt="mapPrompt"
        :map-outputs="[]"
      ></model-interface>
    </div>
  </div>
</template>

<style scoped lang="scss">
#child {
  min-height: inherit;
}
</style>
