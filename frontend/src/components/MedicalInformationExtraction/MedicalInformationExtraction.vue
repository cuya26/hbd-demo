<script>
import {ref} from "vue";
import * as axios from "boot/axios";
import PromptComponent from "components/MedicalInformationExtraction/Prompt.vue";

function applyTemplate(template, userMessage, systemMessage, completionInit) {
  return template
    .replace("{system_message}", systemMessage)
    .replace("{prompt}", userMessage)
    .replace("{completion_init}", completionInit);
}

/* @formatter:on */
export default {
  name: "MedicationExtraction",
  props: ["doc"],
  components: {PromptComponent},
  mounted() {
    this.getProperties("medExt").then((response) => {
      this.medExt.medExtProp = JSON.parse(response.data);
    });
    this.getProperties("medExtFix").then((response) => {
      this.medExt.medExtFixProp = JSON.parse(response.data);
    });
    this.getProperties("timeline").then((response) => {
      this.timeline.timelineProp = JSON.parse(response.data);
    });
    this.getProperties("timelineFix").then((response) => {
      this.timeline.timelineFixProp = JSON.parse(response.data);
    });
    this.getTemplate().then((response) => {
      this.template = response.data;
    });
  },
  data() {
    return {
      template: ref(null),
      medExt: {
        medExtFixProp: ref({}),
        medExtProp: ref({}),
        brokenOutput: false,
        loading: ref(false),
        log: {
          prompt: "",
          answer: "",
          expected: "",
        },
        table: {
          columns: [
            {
              name: "name",
              label: "Name",
              field: "name",
              align: "left",
              sortable: true,
            },
            {
              name: "dose",
              label: "Dose",
              field: "dose",
              align: "left",
              sortable: true,
            },
            {
              name: "frequency",
              label: "Frequency",
              field: "frequency",
              align: "left",
              sortable: true,
            },
            {
              name: "route",
              label: "Route",
              field: "route",
              align: "left",
              sortable: true,
            },
          ],
          rows: ref([]),
        },
        answer: ``,
      },
      timeline: {
        timelineProp: ref({}),
        timelineFixProp: ref({}),
        fixAnswer: {
          fixPromptDialog: ref(false),
        },

        brokenOutput: false,
        loading: ref(false),
        times: [{}],
        answer: "",
      },

      editableTable: ref(false),
      tab: ref("table"),
      showTemplate: ref(false),
      shrinkPrompt: ref(false),
    };
  },
  methods: {
    getTemplate() {
      return axios.api.get("/get_template");
    },

    setProperties(task, properties) {
      axios.api.post("/set_properties/" + task, properties);
    },

    getProperties(task) {
      return axios.api.get("/get_properties/" + task);
    },

    parseMedicationsAnswer(answer) {
      let table = [];
      let lines = answer.split("\n");
      for (let line of lines) {
        if (line.match(/.*?(OUTPUT|END).*?/g)) {
          break;
        }
        if (line.includes(";")) {
          let row = line.split(";");
          table.push({
            name: row[0],
            dose: row[1],
            frequency: row[2],
            route: row[3],
          });
        } else {
          console.log("error parsing medext answer", line);
        }
      }
      return table;
    },

    askLLM(body) {
      return axios.api.post(
        axios.llamaHost + "/v1/completions",
        {
          ...body,
          stream: false,
          stop: ["<|im_end|>"],
        },
        {
          "Content-Type": "application/json",
          timeout: 600000,
        }
      );
    },

    checkNExtractMeds() {
      let str1 = JSON.stringify(this.medExt.table.rows);
      let str2 = JSON.stringify(
        this.parseMedicationsAnswer(this.medExt.answer)
      );
      if (str1 === str2) {
        this.extractMedications();
      } else {
        this.medExt.table.rows = this.parseMedicationsAnswer(
          this.medExt.answer
        );
      }
    },

    async extractMedications() {
      this.medExt.loading = true;
      this.medExt.answer = "";
      let prompt = applyTemplate(
        this.template,
        this.medExt.medExtProp.userMessage,
        this.medExt.medExtProp.systemMessage,
        this.medExt.medExtProp.completionInit
      )
      let parameters = this.medExt.medExtProp.modelParameters
      this.askLLM({
        prompt: prompt.replace("{file}", this.doc),
        stream: true,
        stop: ["<|im_end|>"],
        ...parameters,
      })
        .then((response) => {
          this.medExt.loading = false;
          let answer = response.data.choices[0].text;

          this.medExt.answer = answer;
          this.medExt.table.rows = this.parseMedicationsAnswer(answer);
        })
        .catch((error) => {
          console.error(error);
          this.medExt.loading = false;
          return error.body;
        });
    },

    checkNExtractTimeline() {
      let str1 = JSON.stringify(this.timeline.times);
      let str2 = JSON.stringify(this.parseTimelineAnswer(this.timeline.answer));
      if (str1 === str2) {
        this.extractTimeline();
      } else {
        this.timeline.times = this.parseTimelineAnswer(this.timeline.answer);
      }
    },

    async fixTimelineAnswer() {
      let brokenAnswer = this.timeline.answer;
      let fixPrompt = applyTemplate(
        this.template,
        this.timeline.timelineFixProp.userMessage,
        this.timeline.timelineFixProp.systemMessage,
        this.timeline.timelineFixProp.completionInit
      ).replace("{text}", brokenAnswer);

      this.timeline.loading = true;
      let answer = await this.askLLM({
        prompt: fixPrompt,
        ...this.timeline.timelineFixProp.modelParameters,
      });
      answer = answer.data.choices[0].text;
      this.timeline.loading = false;
      this.timeline.times = this.parseTimelineAnswer(answer);
      this.timeline.answer = answer;
    },

    async fixMedExtAnswer() {
      let brokenAnswer = this.medExt.answer;
      let fixPrompt = this.medExt.fixPrompt.replace("{text}", brokenAnswer);

      this.timeline.loading = true;
      let answer = await this.askLLM({
        prompt: fixPrompt,
        max_tokens: 2048,
        temperature: 0.0,
        mirostat_tau: 3.0,
      });
      answer = answer.data.choices[0].text;
      this.timeline.loading = false;
      this.timeline.times = this.parseTimelineAnswer(answer);
      this.timeline.answer = answer;
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

    startEditingTable(start) {
      this.editableTable = start;
      if (this.editableTable) {
        this.medExt.log.prompt = applyTemplate(
          this.template,
          this.medExt.medExtProp.userMessage,
          this.medExt.medExtProp.systemMessage,
          this.medExt.medExtProp.completionInit
        ).replace("{file}", this.doc);
        this.medExt.log.answer = this.medExt.answer;
      }
    },
    sendLog(task) {
      this.medExt.log.expected = JSON.stringify(this.medExt.table.rows);
      axios.api.post("/log/" + task, this.medExt.log);
    },
    async extractTimeline() {
      this.timeline.loading = true;
      this.timeline.answer = "";
      let prompt = applyTemplate(
        this.template,
        this.timeline.timelineProp.userMessage,
        this.timeline.timelineProp.systemMessage,
        this.timeline.timelineProp.completionInit
      )
      let parameters = this.medExt.medExtProp.modelParameters
      this.askLLM({
        prompt: prompt.replace("{file}", this.doc),
        stream: true,
        stop: ["<|im_end|>"],
        ...parameters,
      })
        .then((response) => {
          let answer = response.data.choices[0].text;
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

    saveMedExt() {
      this.setProperties("medExt", this.medExt.medExtProp);
    },
    saveTimeline() {
      this.setProperties("timeline", this.timeline.timelineProp);
    },
    saveMedExtFix() {
      this.setProperties("medExtFix", this.medExt.medExtFixProp);
    },
    saveTimelineFix() {
      this.setProperties("timelineFix", this.timeline.timelineFixProp);
    },
  },
};
</script>

<template>
  <q-card
    class="relative-position q-pa-none shadow-0 overflow-overlay"
    style="height: 90%"
  >
    <q-card class="full-height column full-width no-wrap">
      <q-tabs
        class="text-grey"
        v-model="tab"
        dense
        active-color="primary"
        active-bg-color="grey-3"
        indicator-color="primary"
        align="justify"
        narrow-indicator
      >
        <q-tab name="table" label="Table"/>
        <q-tab name="timeline" label="Timeline"/>
      </q-tabs>
      <q-separator class="bi-border"/>
      <q-tab-panels
        v-model="tab"
        animated
        class="column no-wrap full-height overflow-hidden"
        style="height: 100%"
      >
        <q-tab-panel name="table" class="column full-height q-ma-none no-wrap">
          <div
            v-if="medExt.loading === true"
            class="absolute-top-left bg-grey-3 row justify-center items-center"
            style="height: 100%; width: 100%; z-index: 10; opacity: 50%"
          >
            <q-spinner-gears color="primary" size="8em"/>
          </div>
          <div class="flex justify-between">
            <div>
              <q-btn
                class="q-ma-sm"
                color="primary"
                @click="checkNExtractMeds()"
              >Extract medications
              </q-btn>

              <q-btn-dropdown
                :disable-main-btn="!medExt.brokenOutput"
                split
                class="q-ma-sm"
                color="secondary"
                @click="fixMedExtAnswer()"
                label="Fix structure with llm"
              >
                <q-list>
                  <q-item
                    clickable
                    v-close-popup
                    @click="timeline.fixAnswer.fixPromptDialog = true"
                  >
                    <q-item-section>
                      <q-item-label>Edit fix prompt</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>

              <q-dialog v-model="timeline.fixAnswer.fixPromptDialog">
                <q-card
                  style="width: 50%; height: 50%"
                  class="flex column justify-between"
                >
                  <q-card-section>
                    <prompt-component
                      ref="fixPromptComponent"
                      :template="template"
                      v-model:user-message="medExt.medExtFixProp.userMessage"
                      v-model:completion-init="
                        medExt.medExtFixProp.completionInit
                      "
                      v-model:system-message="
                        medExt.medExtFixProp.systemMessage
                      "
                      v-model:model-settings="
                        medExt.medExtFixProp.modelParameters
                      "
                      :enable-answer="false"
                      :enable-send="false"
                    >
                    </prompt-component>
                  </q-card-section>

                  <!-- Notice v-close-popup -->
                  <q-card-actions align="right">
                    <q-btn flat label="Cancel" color="primary" v-close-popup/>
                    <q-btn
                      flat
                      label="Save"
                      @click="saveMedExtFix()"
                      color="primary"
                      v-close-popup
                    />
                  </q-card-actions>
                </q-card>
              </q-dialog>
              <q-toggle
                v-show="medExt.table.rows.length > 0"
                :model-value="editableTable"
                @update:model-value="startEditingTable($event)"
                color="primary"
                icon="edit"
                label="Edit table"
              />
              <q-btn
                v-if="editableTable"
                @click="sendLog('medExt')"
                class="q-ma-sm"
              >
                Save log
              </q-btn>
            </div>
            <q-btn class="q-ma-sm" @click="saveMedExt">Save Settings</q-btn>
          </div>
          <q-table
            class="col col-grow"
            title="Medications"
            :rows="medExt.table.rows"
            :columns="medExt.table.columns"
            row-key="name"
            :rows-per-page-options="[0, 10, 20, 30]"
          >
            <template v-slot:body="props">
              <q-tr :props="props">
                <q-td key="name" :props="props">
                  {{ props.row.name }}
                  <q-popup-edit
                    :disable="!editableTable"
                    v-model="props.row.name"
                    v-slot="scope"
                  >
                    <q-input
                      v-model="scope.value"
                      dense
                      autofocus
                      title="Update Name"
                      @keyup.enter="scope.set"
                    />
                  </q-popup-edit>
                </q-td>
                <q-td key="dose" :props="props">
                  {{ props.row.dose }}
                  <q-popup-edit
                    :disable="!editableTable"
                    v-model="props.row.dose"
                    v-slot="scope"
                  >
                    <q-input
                      v-model="scope.value"
                      dense
                      autofocus
                      title="Update dosage"
                      @keyup.enter="scope.set"
                    />
                  </q-popup-edit>
                </q-td>
                <q-td key="frequency" :props="props">
                  {{ props.row.frequency }}
                  <q-popup-edit
                    :disable="!editableTable"
                    v-model="props.row.frequency"
                    v-slot="scope"
                  >
                    <q-input
                      v-model="scope.value"
                      dense
                      autofocus
                      title="Update dosage"
                      @keyup.enter="scope.set"
                    />
                  </q-popup-edit>
                </q-td>
                <q-td key="route" :props="props">
                  {{ props.row.route }}
                  <q-popup-edit
                    :disable="!editableTable"
                    v-model="props.row.route"
                    v-slot="scope"
                  >
                    <q-input
                      v-model="scope.value"
                      dense
                      autofocus
                      title="Update dosage"
                      @keyup.enter="scope.set"
                    />
                  </q-popup-edit>
                </q-td>
              </q-tr>
            </template>
          </q-table>
          <div>
            <prompt-component
              ref="medExtPromptComponent"
              :accordion="true"
              :template="template"
              v-model:answer="medExt.answer"
              v-model:completion-init="medExt.medExtProp.completionInit"
              v-model:system-message="medExt.medExtProp.systemMessage"
              v-model:user-message="medExt.medExtProp.userMessage"
              v-model:model-settings="medExt.medExtProp.modelParameters"
              @askLLM="extractMedications"
              @clear-output="medExt.answer = ''"
              @answer-changed="medExt.answer = $event"
            ></prompt-component>
          </div>
        </q-tab-panel>
        <q-tab-panel name="timeline">
          <div
            v-if="timeline.loading === true"
            class="absolute-top-left bg-grey-3 row justify-center items-center"
            style="height: 100%; width: 100%; z-index: 10; opacity: 50%"
          >
            <q-spinner-gears color="primary" size="8em"/>
          </div>
          <div class="q-pa-lg">
            <div class="flex justify-between">
              <div class="flex">
                <q-btn
                  class="q-ma-sm"
                  color="primary"
                  @click="checkNExtractTimeline()"
                >Extract timeline
                </q-btn>

                <q-btn-dropdown
                  :disable-main-btn="!timeline.brokenOutput"
                  split
                  class="q-ma-sm"
                  color="secondary"
                  @click="fixTimelineAnswer()"
                  label="Fix structure with llm"
                >
                  <q-list>
                    <q-item
                      clickable
                      v-close-popup
                      @click="timeline.fixAnswer.fixPromptDialog = true"
                    >
                      <q-item-section>
                        <q-item-label>Edit fix prompt</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-btn-dropdown>

                <q-dialog v-model="timeline.fixAnswer.fixPromptDialog">
                  <q-card
                    style="width: 50%; height: 50%"
                    class="flex column justify-between"
                  >
                    <q-card-section>
                      <prompt-component
                        ref="fixPromptComponent"
                        :template="template"
                        v-model:user-message="
                          timeline.timelineFixProp.userMessage
                        "
                        v-model:completion-init="
                          timeline.timelineFixProp.completionInit
                        "
                        v-model:system-message="
                          timeline.timelineFixProp.systemMessage
                        "
                        v-model:model-settings="
                          timeline.timelineFixProp.modelParameters
                        "
                        :enable-answer="false"
                        :enable-send="false"
                      >
                      </prompt-component>
                    </q-card-section>

                    <!-- Notice v-close-popup -->
                    <q-card-actions align="right">
                      <q-btn
                        flat
                        label="Cancel"
                        color="primary"
                        v-close-popup
                      />
                      <q-btn
                        flat
                        label="Save"
                        color="primary"
                        @click="saveTimelineFix()"
                        v-close-popup
                      />
                    </q-card-actions>
                  </q-card>
                </q-dialog>
              </div>
              <q-btn class="q-ma-sm" @click="saveTimeline()"
              >Save Settings
              </q-btn
              >
            </div>
          </div>

          <q-timeline layout="comfortable" side="right" color="secondary">
            <q-timeline-entry heading>Timeline</q-timeline-entry>

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
          <div>
            <prompt-component
              ref="timelinePromptComponent"
              :template="template"
              :answer="timeline.answer"
              v-model:system-message="timeline.timelineProp.systemMessage"
              v-model:user-message="timeline.timelineProp.userMessage"
              v-model:completion-init="timeline.timelineProp.completionInit"
              v-model:model-settings="timeline.timelineProp.modelParameters"
              @askLLM="extractTimeline"
              @clear-output="timeline.answer = ''"
              @answer-changed="timeline.answer = $event"
            ></prompt-component>
          </div>
        </q-tab-panel>
        <q-tab-panel name="chat"></q-tab-panel>
      </q-tab-panels>
    </q-card>
  </q-card>
</template>

<style scoped lang="scss">
::-webkit-scrollbar {
  display: none;
}
</style>
