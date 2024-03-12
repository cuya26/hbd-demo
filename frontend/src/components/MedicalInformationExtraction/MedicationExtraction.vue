<script>
import { useQuasar } from "quasar";
import { ref } from "vue";
import PromptComponent from "./Prompt.vue";

import InformationSourceLocalization from "components/MedicalInformationExtraction/InformationSourceLocalization.vue";
import SaveDialog from "components/MedicalInformationExtraction/TasksDialog.vue";
import {
  applyTemplate,
  askLLM,
  getProperties,
  getTasks,
  getTemplate,
  setProperties,
} from "components/MedicalInformationExtraction/utils";

// prettier-ignore
const columns = [
  {name: "name", label: "Name", field: "name", align: "left", sortable: true},
  {name: "dose", label: "Dose", field: "dose", align: "left", sortable: true},
  {name: "frequency", label: "Frequency", field: "frequency", align: "left", sortable: true},
  {name: "route", label: "Route", field: "route", align: "left", sortable: true},
  {name: "lines", label: "Lines", field: "lines", align: "left", sortable: false},
]

export default {
  name: "MedicationExtraction",
  components: { PromptComponent },
  props: { doc: String, show: Boolean },
  watch: {
    show: function (val) {
      this.$nextTick(function () {
        this.$refs.medExtPromptComponent.updateHeights();
      });
    },
  },

  mounted() {
    getProperties(this.medExt.taskName).then((response) => {
      this.medExt.medExtProp = JSON.parse(response.data);
    });
    getProperties("medExtFix").then((response) => {
      this.medExt.medExtFixProp = JSON.parse(response.data);
    });
    getTemplate().then((response) => {
      this.template = response.data;
    });
  },
  data() {
    return {
      separator: ref(";"),
      template: ref(""),
      $q: useQuasar(),
      tasks: [],
      editableTable: ref(false),

      medExt: {
        fixAnswer: {
          fixPromptDialog: ref(false),
        },
        taskName: "medExtIta",
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
          columns: columns,
          rows: ref([]),
        },
        answer: "",
      },
    };
  },
  methods: {
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

    async fixMedExtAnswer() {
      let brokenAnswer = this.medExt.answer;
      let fixPrompt = this.medExt.fixPrompt.replace("{text}", brokenAnswer);

      this.timeline.loading = true;
      let answer = await askLLM({
        prompt: fixPrompt,
        max_tokens: 2048,
        temperature: 0.0,
        mirostat_tau: 3.0,
      });
      this.timeline.loading = false;
      this.timeline.times = this.parseTimelineAnswer(answer);
      this.timeline.answer = answer;
    },

    async extractMedications() {
      this.medExt.loading = true;
      this.medExt.answer = "";
      let prompt = applyTemplate(
        this.template,
        this.medExt.medExtProp.userMessage,
        this.medExt.medExtProp.systemMessage,
        this.medExt.medExtProp.completionInit
      );
      let parameters = this.medExt.medExtProp.modelParameters;
      let file = this.doc.split("\n");
      for (let i = 0; i < file.length; i++) {
        file[i] = ("" + i).padStart(4, " ") + "| " + file[i];
      }
      askLLM({
        prompt: prompt.replace("{file}", file.join("\n")),
        ...parameters,
      })
        .then((text) => {
          console.log(text);
          this.medExt.loading = false;
          this.medExt.answer = text;
          this.medExt.table.rows = this.parseMedicationsAnswer(text);
        })
        .catch((error) => {
          console.error(error);
          this.medExt.loading = false;
          return error.body;
        });
    },

    parseMedicationsAnswer(answer) {
      let table = [];
      let lines = answer.split("\n");
      for (let line of lines) {
        if (line.match(/.*?(OUTPUT|END).*?/g)) {
          break;
        }
        if (line.includes(this.separator)) {
          let row = line.split(this.separator);
          table.push({
            name: row[0],
            dose: row[1],
            frequency: row[2],
            route: row[3],
            lines: (row[4] ?? "").split(",").map((x) => parseInt(x)),
          });
        } else {
          console.log("error parsing medext answer", line);
        }
      }
      return table;
    },
    openLoadDialog(save = true) {
      let dialogRef = this.$q.dialog({
        component: SaveDialog,
        // props forwarded to your custom component
        componentProps: {
          taskName: this.medExt.taskName,
          tasks: this.tasks,
          save: save,

          onSetTask: (data) => {
            this.medExt.taskName = data;
            dialogRef.update({
              taskName: this.medExt.taskName,
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
            this.medExt.medExtProp = JSON.parse(response.data);
            this.$refs.medExtPromptComponent.updateHeights();
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
          setProperties(taskName, this.medExt.medExtProp);
        })
        .onCancel(() => {
          console.log("Cancel");
        });
    },
    saveMedExtFix() {
      setProperties("medExtFix", this.medExt.medExtFixProp);
    },
    openInformationSourceLocalization() {
      this.$q
        .dialog({
          component: InformationSourceLocalization,
          fullWidth: true,
          fullHeight: true,
          // props forwarded to your custom component
          componentProps: {
            rows: this.medExt.table.rows,
            columns: this.medExt.table.columns,
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
  <div
    id="child"
    class="q-pa-md full-height column flex q-ma-none no-wrap"
    style="height: 100% !important; flex-shrink: 0"
  >
    <div>
      <div
        v-if="medExt.loading === true"
        class="absolute-top-left bg-grey-3 row justify-center items-center"
        style="height: 100%; width: 100%; z-index: 10; opacity: 50%"
      >
        <q-spinner-gears color="primary" size="8em" />
      </div>
      <q-table
        class="col col-grow"
        title="Medications"
        :rows="
          medExt.table.rows.length > 0
            ? medExt.table.rows.length
            : [
                {
                  name: 'No Data',
                  dose: '',
                  frequency: '',
                  route: '',
                  lines: [],
                },
              ]
        "
        :columns="medExt.table.columns"
        row-key="name"
        :rows-per-page-options="[0, 10, 20, 30]"
      >
        <template v-slot:top>
          <div class="col-2 q-table__title">Medications</div>
          <q-space />
          <q-input v-model="separator" label="Separator" dense />
        </template>
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
      <div class="flex justify-between q-py-sm">
        <div class="flex items-center" style="gap: 0.8em">
          <q-btn class="" color="primary" @click="checkNExtractMeds()"
            >Extract medications
          </q-btn>
          <q-toggle
            v-show="medExt.table.rows.length > 0"
            :model-value="editableTable"
            @update:model-value="startEditingTable($event)"
            color="primary"
            icon="edit"
            label="Edit table"
          />
          <q-btn
            v-if="medExt.table.rows.length > 0"
            @click="this.openInformationSourceLocalization"
            >See source localization
          </q-btn>
          <q-btn
            v-if="editableTable"
            @click="sendLog('medExt')"
            class="q-ma-sm"
          >
            Save log
          </q-btn>
        </div>

        <div class="flex items-center" style="gap: 0.8em">
          <q-btn class="" @click="loadMedExt">Load Settings</q-btn>
          <q-btn class="" @click="saveMedExt">Save Settings</q-btn>
        </div>
      </div>
    </div>
    <div class="col-grow">
      <div class="col-grow"></div>
    </div>
    <div>
      <prompt-component
        ref="medExtPromptComponent"
        :accordion="true"
        v-model:template="template"
        v-model:answer="medExt.answer"
        v-model:completion-init="medExt.medExtProp.completionInit"
        v-model:system-message="medExt.medExtProp.systemMessage"
        v-model:user-message="medExt.medExtProp.userMessage"
        v-model:model-settings="medExt.medExtProp.modelParameters"
        @askLLM="extractMedications"
        @clear-output="medExt.answer = ''"
      ></prompt-component>
    </div>
  </div>
</template>

<style scoped lang="scss">
#child {
  min-height: inherit;
}
</style>
