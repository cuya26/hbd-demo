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
        taskName: "ISLTimelineItaThree2",
        timelineProp: ref({}),
        timelineFixProp: ref({}),
        fixAnswer: {
          fixPromptDialog: ref(false),
        },

        brokenOutput: false,
        loading: ref(false),
        times:

          [
            {
              "dateValue": "2020-12-10",
              "dateString": "December 10, 2020",
              "description": "Accesso c/o PS di Vimercate per dolore toracico altalenante",
              "line": 29
            },
            {
              "dateValue": "2020-12-11",
              "dateString": "November 11, 2020",
              "description": "Ecocardiogramma eseguito in acuto",
              "line": 31
            },
            {
              "dateValue": "2020-12-09",
              "dateString": "December 9, 2020",
              "description": "EcoTSA",
              "line": 50
            },
            {
              "dateValue": "2021-01-01",
              "dateString": "January 1, 2021",
              "description": "Fever serotina",
              "line": 51
            },
            {
              "dateValue": "2021-01-02",
              "dateString": "January 2, 2021",
              "description": "Fever serotina",
              "line": 52
            },
            {
              "dateValue": "2021-01-03",
              "dateString": "January 3, 2021",
              "description": "Tampone per SARS-COV2 c/o nostro Centro",
              "line": 61
            },
            {
              "dateValue": "2021-01-04",
              "dateString": "January 4, 2021",
              "description": "Tampone per Sars-Cov2 e sierologia per Sars-Cov2",
              "line": 62
            },
            {
              "dateValue": "2021-01-05",
              "dateString": "January 5, 2021",
              "description": "Intervento cardiochirurgico",
              "line": 79
            },
            {
              "dateValue": "2021-01-07",
              "dateString": "January 7, 2021",
              "description": "Rientro in reparto",
              "line": 89
            },
            {
              "dateValue": "2021-01-10",
              "dateString": "January 10, 2021",
              "description": "Rx torace",
              "line": 98
            },
            {
              "dateValue": "2021-01-11",
              "dateString": "January 11, 2021",
              "description": "Ecocardiogramma TT",
              "line": 101
            },
            {
              "dateValue": "2021-01-12",
              "dateString": "January 12, 2021",
              "description": "Dimissione",
              "line": 112
            }
          ]
        ,
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
  <div class="full-width full-height flip-card">
    <div
      class="full-width full-height flip-card-inner"
      :class="{ rotate: showSettings }"
    >
      <div
        id="child"
        class="full-height flip-card-front q-pa-md column justify-between full-width no-wrap"
      >
        <div
          class="column no-wrap full-height overflow-auto"
          style="height: 100%"
        >
          <q-btn
            class="q-ma-sm"
            style="width: 30%; min-width: fit-content"
            color="primary"
            @click="this.$refs.timelinePromptComponent.sendLLM()"
          >Extract timeline
          </q-btn>
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
          <div class="full-width text-left">


          <q-timeline layout="dense" side="right" color="secondary">
            <q-timeline-entry v-if="timeline.times.length === 0">
            </q-timeline-entry>
            <q-timeline-entry
              v-for="time in timeline.times"
              :key="time"
              :title="time.dateString"
              side="left"
              class="q-pa-none"
            >
              <p class="text-left q-ma-none">
                {{
                  time.description
                }}
              </p>
            </q-timeline-entry>
          </q-timeline>
          </div>

          <div class="q-pa-lg">
            <div class="flex justify-between">
              <div class="flex justify-between">
                <div class="flex items-center" style="gap: 0.8em">

                  <q-btn
                    v-if="timeline.times.length > 0"
                    @click="this.openInformationSourceLocalization"
                    >View Times Locations
                  </q-btn>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="q-pa-md flex column full-height flip-card-back">
        <div class="flex col-1 full-width justify-between">
          <h6 style="margin: 0">Timeline Extraction Settings</h6>
          <q-icon name="close" @click="showSettings = false" />
        </div>
        <model-interface
          class="col"
          ref="timelinePromptComponent"
          :enable-send="false"
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
  </div>
</template>

<style scoped lang="scss">
#child {
  min-height: inherit;
}


.flip-card {
  background-color: transparent;
  perspective: 4000px;
}

.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform .5s;
  transform-style: preserve-3d;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
}

.flip-card .flip-card-inner.rotate {
  transform: rotateY(180deg);
}

.flip-card-front,
.flip-card-back {
  position: absolute;
  transform: rotateX(0deg);
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

.flip-card-back {
  transform: rotateY(180deg);
}

</style>
