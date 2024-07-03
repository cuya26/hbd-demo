<script>
import { useQuasar } from "quasar";
import { ref } from "vue";
// import PromptComponent from "./ModelInterface.vue";
import InformationSourceLocalization from "components/MedicalInformationExtraction/InformationSourceLocalization.vue";
import SaveDialog from "components/MedicalInformationExtraction/TasksDialog.vue";
import {
  applyTemplate,
  getProperties,
  getTasks,
  setProperties,
} from "components/MedicalInformationExtraction/utils";
import ModelInterface from "components/MedicalInformationExtraction/ModelInterface.vue";
import * as axios from "boot/axios";


// prettier-ignore
const columns = [
  {name: "name", label: "Name", field: "name", align: "left", sortable: true},
  {name: "dose", label: "Dose", field: "dose", align: "left", sortable: true},
  {name: "route", label: "Mode", field: "route", align: "left", sortable: true},
  {name: "frequency", label: "Frequency", field: "frequency", align: "left", sortable: true},
  {name: "lines", label: "Lines", field: "lines", align: "left", sortable: false},
]

export default {
  name: "MedicationExtraction",
  components: { ModelInterface },
  // components: { PromptComponent },
  props: { doc: String, show: Boolean },
  watch: {
    show: function (val) {
      this.$nextTick(function () {});
    },
  },

  mounted() {
    getProperties(this.medExt.taskName).then((response) => {
      this.medExtSettings = JSON.parse(response.data);
    });
    this.medExt.table.rows = this.parseMedicationsAnswer(this.medExt.answer)
  },
  data() {
    return {
      $q: useQuasar(),
      tasks: [],
      template: ref(""),
      editableTable: ref(false),
      medExtSettings: ref({}),
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
      separator: ref(";"),
      medExt: {
        taskName: "medExtIta",
        medExtProp: ref({}),
        medExtFixProp: ref({}),
        fixAnswer: {
          fixPromptDialog: ref(false),
        },
        log: {
          prompt: "",
          answer: "",
          expected: "",
        },
        brokenOutput: false,
        loading: ref(false),
        table: {
          columns: columns,
          rows: ref([]),
        },
        answer: "",
      },
    };
  },
  methods: {
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
      let obj1 =  JSON.stringify(this.medExt.table.rows)
      let obj2 =  JSON.stringify(this.parseMedicationsAnswer(this.medExt.answer))

      if(obj1 === obj2)
      {
        Promise.resolve().then(() =>
        this.$q.notify({
          message: `Please edit table before send log`,
          color: 'orange',
          position: 'top-right',
          actions: [
            { label: 'Dismiss', color: 'white', handler: () => { /* ... */ } }
          ]
        }))
        return
      }
      this.medExt.log.expected = JSON.stringify(this.medExt.table.rows);

      axios.api.post("/log/" + task, this.medExt.log)
        .then(({data}) =>{
        this.$q.notify({
          message: `Data has been sent`,
          color: 'green',
          position: 'top-right',
          actions: [
            { label: 'Dismiss', color: 'white', handler: () => { /* ... */ } }
          ]
        }
      )})
        .catch((err) =>
          this.$q.notify({
            message: `Error: ${err}`,
            color: 'red',
            position: 'top-right',
            actions: [
              { label: 'Dismiss', color: 'white', handler: () => { /* ... */ } }
            ]
          })
        )
    },

    parseMedicationsAnswer(answer) {
      let table = [];
      let lines = answer.split("\n");
      for (let line of lines) {
        if (line.match(/.*?(OUTPUT|END|```).*?/g)) {
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
            // this.$refs.medExtPromptComponent.updateHeights();
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
    toggleSettings() {
      this.showSettings = !this.showSettings;
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
  <div class="full-width full-height flip-card">
    <div
      class="full-width full-height flip-card-inner"
      :class="{ rotate: showSettings }"
    >
      <div
        id="child"
        class="q-pa-md full-height column flex q-ma-none no-wrap flip-card-front"
        style="height: 100% !important; flex-shrink: 0"
      >
        <q-btn
          class="q-mb-sm"
          style="width: 30%; min-width: fit-content"
          color="primary"
          @click="this.$refs.medExtPromptComponent.sendLLM()"
        >Extract medications
        </q-btn>
        <div class="flex full-width justify-between">
          <h6 style="margin: 0">Medications</h6>
          <q-icon name="settings" @click="showSettings = !showSettings" />
        </div>

        <div>
          <div
            v-if="medExt.loading === true"
            class="absolute-top-left bg-grey-3 row justify-center items-center"
            style="height: 100%; width: 100%; z-index: 10; opacity: 50%"
          >
            <q-spinner-gears color="primary" size="8em" />
          </div>

          <q-table
            dense
            class="col col-grow"
            :rows="
              medExt.table.rows.length > 0
                ? medExt.table.rows
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
            :columns="medExt.table.columns.slice(0, -1)"
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
          <div class="flex justify-between q-py-sm">
            <div class="flex items-center" style="gap: 0.8em">

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
                >View Medication Locations
              </q-btn>
              <q-btn
                v-if="editableTable"
                @click="sendLog('medExt')"
                class="q-ma-sm"
              >
                Save log
              </q-btn>
            </div>
          </div>
        </div>
      </div>
      <div class="q-pa-md flex column flip-card-back full-height">
        <div class="flex col-1 full-width justify-between">
          <h6 style="margin: 0">Medication Extraction Settings</h6>
          <q-icon name="close" @click="showSettings = false" />
        </div>
        <model-interface
          class="col"
          ref="medExtPromptComponent"
          :enable-send="false"
          v-model:settings="medExtSettings"
          v-model:answer="medExt.answer"
          @loading="medExt.loading = $event"
          @update:answer="
            this.medExt.table.rows = this.parseMedicationsAnswer(
              this.medExt.answer
            )
          "
          :map-prompt="mapPrompt"
          :map-outputs="[]"
        ></model-interface>
        <q-input class="col-1" v-model="separator" label="Separator" dense />
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
