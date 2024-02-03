<script>
import { ref } from "vue";
import PromptComponent from "./Prompt.vue";
import {
  applyTemplate,
  askLLM,
  getProperties,
  getTasks,
  getTemplate,
  setProperties,
} from "components/MedicalInformationExtraction/utils";
import SaveDialog from "components/MedicalInformationExtraction/TasksDialog.vue";
import ISLTimeline from "components/MedicalInformationExtraction/ISLTimeline.vue";

export default {
  name: "TimelineExtraction",
  components: { PromptComponent },
  props: { doc: String, show: Boolean },
  watch: {
    show: function (val) {
      this.$nextTick(() => {
        this.$refs.timelinePromptComponent.updateHeights();
      });
    },
  },

  mounted() {
    getProperties(this.timeline.taskName).then((response) => {
      this.timeline.timelineProp = JSON.parse(response.data);
    });
    getProperties("timelineFix").then((response) => {
      this.timeline.timelineFixProp = JSON.parse(response.data);
    });
    getTemplate().then((response) => {
      this.template = response.data;
    });
  },
  data() {
    return {
      tasks: [],
      template: ref(""),
      timeline: {
        taskName: "ISLTimelineIta",
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
      let res = [];
      this.timeline.brokenOutput = false;
      try {
        res = JSON.parse(answer);
      } catch (e) {
        console.log("error parsing timeline answer");
        this.timeline.brokenOutput = true;
        res = [{}];
      }
      return res;
    },

    async extractTimeline() {
      this.timeline.loading = true;
      this.timeline.answer = "";
      let prompt = applyTemplate(
        this.template,
        this.timeline.timelineProp.userMessage,
        this.timeline.timelineProp.systemMessage,
        this.timeline.timelineProp.completionInit
      );
      let parameters = this.timeline.timelineProp.modelParameters;
      let file = this.doc.split("\n");
      for (let i = 0; i < file.length; i++) {
        file[i] = ("" + i).padStart(4, " ") + "| " + file[i];
      }
      askLLM({
        prompt: prompt.replace("{file}", file),
        ...parameters,
      })
        .then((text) => {
          let answer = text;
          this.timeline.loading = false;
          this.timeline.answer = answer;
          this.timeline.times = this.parseTimelineAnswer(answer);
        })
        .catch((error) => {
          console.error(error);
          this.timeline.loading = false;
          return error.body;
        });
    },

    openLoadDialog(save = true) {
      let dialogRef = this.$q.dialog({
        component: SaveDialog,
        // props forwarded to your custom component
        componentProps: {
          taskName: this.timeline.taskName,
          tasks: this.tasks,
          save: save,

          onSetTask: (data) => {
            this.timeline.taskName = data;
            dialogRef.update({
              taskName: this.timeline.taskName,
            });
          },
          // ...more..props...
        },
      });
      getTasks().then((response) => {
        this.tasks = response.data;
        dialogRef.update({
          tasks: this.tasks,
        });
      });
      return dialogRef;
    },
    loadMedExt() {
      let dialogRef = this.openLoadDialog(false);
      dialogRef
        .onOk((taskName) => {
          console.log("OK");
          getProperties(taskName).then((response) => {
            this.timeline.timelineProp = JSON.parse(response.data);
            this.$refs.timelinePromptComponent.updateHeights();
          });
        })
        .onCancel(() => {
          console.log("Cancel");
        });
    },
    saveMedExt() {
      let dialogRef = this.openLoadDialog(true);
      dialogRef
        .onOk((taskName) => {
          console.log("OK");
          setProperties(taskName, this.timeline.timelineProp);
        })
        .onCancel(() => {
          console.log("Cancel");
        });
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
  <q-card class="full-height column full-width no-wrap">
    <div
      class="column no-wrap full-height overflow-hidden"
      style="height: 100%"
    >
      <div
        v-if="timeline.loading === true"
        class="absolute-top-left bg-grey-3 row justify-center items-center"
        style="height: 100%; width: 100%; z-index: 10; opacity: 50%"
      >
        <q-spinner-gears color="primary" size="8em" />
      </div>

      <q-timeline layout="comfortable" side="right" color="secondary">
        <q-timeline-entry heading>Timeline</q-timeline-entry>
        <q-timeline-entry v-if="timeline.times.length === 0">
        </q-timeline-entry>
        <q-timeline-entry
          v-for="time in timeline.times"
          :key="time"
          :subtitle="time.time"
          :title="time.headline"
        >
          <ul>
            <li v-for="event in time.events" :key="event">
              {{ event }}
            </li>
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
                @click="checkNExtractTimeline()"
                >Extract timeline
              </q-btn>
              <q-btn
                v-if="timeline.times.length > 0"
                @click="this.openInformationSourceLocalization"
                >See source localization
              </q-btn>
            </div>

            <!--            <q-btn-dropdown-->
            <!--              :disable-main-btn="!timeline.brokenOutput"-->
            <!--              split-->
            <!--              class="q-ma-sm"-->
            <!--              color="secondary"-->
            <!--              @click="fixTimelineAnswer()"-->
            <!--              label="Fix structure with llm"-->
            <!--            >-->
            <!--              <q-list>-->
            <!--                <q-item-->
            <!--                  clickable-->
            <!--                  v-close-popup-->
            <!--                  @click="timeline.fixAnswer.fixPromptDialog = true"-->
            <!--                >-->
            <!--                  <q-item-section>-->
            <!--                    <q-item-label>Edit fix prompt</q-item-label>-->
            <!--                  </q-item-section>-->
            <!--                </q-item>-->
            <!--              </q-list>-->
            <!--            </q-btn-dropdown>-->

            <!--            <q-dialog v-model="timeline.fixAnswer.fixPromptDialog">-->
            <!--              <q-card-->
            <!--                style="width: 50%; height: 50%"-->
            <!--                class="flex column justify-between"-->
            <!--              >-->
            <!--                <q-card-section>-->
            <!--                  <prompt-component-->
            <!--                    ref="fixPromptComponent"-->
            <!--                    v-model:template="template"-->
            <!--                    v-model:user-message="timeline.timelineFixProp.userMessage"-->
            <!--                    v-model:completion-init="-->
            <!--                      timeline.timelineFixProp.completionInit-->
            <!--                    "-->
            <!--                    v-model:system-message="-->
            <!--                      timeline.timelineFixProp.systemMessage-->
            <!--                    "-->
            <!--                    v-model:model-settings="-->
            <!--                      timeline.timelineFixProp.modelParameters-->
            <!--                    "-->
            <!--                    :enable-answer="false"-->
            <!--                    :enable-send="false"-->
            <!--                  >-->
            <!--                  </prompt-component>-->
            <!--                </q-card-section>-->

            <!--                &lt;!&ndash; Notice v-close-popup &ndash;&gt;-->
            <!--                <q-card-actions align="right">-->
            <!--                  <q-btn flat label="Cancel" color="primary" v-close-popup />-->
            <!--                  <q-btn-->
            <!--                    flat-->
            <!--                    label="Save"-->
            <!--                    color="primary"-->
            <!--                    @click="saveTimelineFix()"-->
            <!--                    v-close-popup-->
            <!--                  />-->
            <!--                </q-card-actions>-->
            <!--              </q-card>-->
            <!--            </q-dialog>-->
          </div>
          <div class="flex items-center" style="gap: 0.8em">
            <q-btn class="" @click="loadMedExt">Load Settings</q-btn>
            <q-btn class="" @click="saveMedExt">Save Settings</q-btn>
          </div>
        </div>
      </div>
      <div>
        <prompt-component
          ref="timelinePromptComponent"
          v-model:template="template"
          v-model:answer="timeline.answer"
          v-model:system-message="timeline.timelineProp.systemMessage"
          v-model:user-message="timeline.timelineProp.userMessage"
          v-model:completion-init="timeline.timelineProp.completionInit"
          v-model:model-settings="timeline.timelineProp.modelParameters"
          @askLLM="extractTimeline"
          @clear-output="timeline.answer = ''"
          @answer-changed="timeline.answer = $event"
        ></prompt-component>
      </div>
    </div>
  </q-card>
</template>

<style scoped lang="sass"></style>
