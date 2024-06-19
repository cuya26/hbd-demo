<script>
import { ref } from "vue";
import PromptTemplate from "components/MedicalInformationExtraction/PromptTemplate.vue";
import * as utils from "components/MedicalInformationExtraction/utils";
import {
  getProperties,
  getTasks,
  sanitizeTemplate,
  setProperties,
} from "components/MedicalInformationExtraction/utils";
import SaveDialog from "components/MedicalInformationExtraction/TasksDialog.vue";

export default {
  name: "ModelInterface",
  components: { PromptTemplate },
  // components: {  },
  props: {
    settings: Object,
    answer: String,
    accordion: Boolean,
    mapOutputs: Array,
    mapPrompt: Array,
    enableSend: Boolean,
  },
  watch: {
    settings: function (newVal) {
      console.log(newVal);
      this.settingsLocal = newVal;
      this.settingsLocal.template = sanitizeTemplate(
        this.settingsLocal.template
      );
    },

    answer: function (val) {
      setTimeout(() => {
        this.adjustHeight(this.$refs.systemMessage);
      });
    },
    modelSettings: function (newVal, oldVal) {
      for (const [key, value] of Object.entries(newVal)) {
        this.updateSetting(key, value);
      }
    },
    systemMessage: function (val) {
      setTimeout(() => {
        this.adjustHeight(this.$refs.systemMessage);
      });
    },
    userMessage: function (val) {
      setTimeout(() => {
        this.adjustHeight(this.$refs.userMessage);
      });
    },
    completionInit: function (val) {
      setTimeout(() => {
        this.adjustHeight(this.$refs.completionInit);
      });
    },
  },
  emits: ["update:settings", "update:answer", "loading"],

  methods: {
    openLoadDialog(save = true) {
      let dialogRef = this.$q.dialog({
        component: SaveDialog,
        // props forwarded to your custom component
        componentProps: {
          taskName: this.settingsLocal.taskName,
          tasks: this.tasks,
          save: save,

          onSetTask: (data) => {
            this.settingsLocal.taskName = data;
            dialogRef.update({
              taskName: this.settingsLocal.taskName,
            });
          },
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

    loadSettings() {
      let dialogRef = this.openLoadDialog(false);
      dialogRef
        .onOk((taskName) => {
          console.log("OK");
          getProperties(taskName).then((response) => {
            this.settingsLocal = JSON.parse(response.data);
            // this.$refs.timelinePromptComponent.updateHeights();
          });
        })
        .onCancel(() => {
          console.log("Cancel");
        });
    },
    saveSettings() {
      let dialogRef = this.openLoadDialog(true);
      dialogRef
        .onOk((taskName) => {
          console.log("OK");
          setProperties(taskName, this.settingsLocal);
        })
        .onCancel(() => {
          console.log("Cancel");
        });
    },

    addStep() {
      this.settingsLocal.steps ??= [];
      this.settingsLocal.steps.push({
        name: "Step " + (this.settingsLocal.steps.length + 1),
        systemMessage: "",
        userMessage: "",
        completionInit: "",
      });
      this.tab = "Step " + this.settingsLocal.steps.length;
    },
    removeStep(tab) {
      let index = this.settingsLocal.steps.findIndex((step) => {
        return step.name === tab;
      });
      if (index === -1) return;
      this.settingsLocal.steps.splice(index, 1);
      this.settingsLocal.steps = this.settingsLocal.steps.map((step, i) => {
        step.name = "Step " + (i + 1);
        return step;
      });
      setTimeout(() => {
        this.tab = "Step " + Math.min(this.settingsLocal.steps.length, index);
      });
    },

    updateHeights() {
      for (let ref in this.$refs.promptTemplate) {
        this.$refs.promptTemplate[ref].updateHeights();
      }
    },

    adjustHeight(element) {
      if (!element) return;
      element.style.height = 0 + "px";
      element.style.height = element.scrollHeight + "px";
    },
    updateSetting(key, value) {
      this.modelParameters[key].model = value;
      this.modelParameters[key].enabled = true;
      this.settingsLocal.modelParameters[key] = value;
      this.updateSettings();
    },
    updateTemplate(key, value) {
      this.settingsLocal.template[key] = value;
      this.updateSettings();
    },

    updateSettings() {
      this.$emit("update:settings", this.settingsLocal);
    },

    async sendLLM() {
      let answer = "";
      let prevMessage = "";
      this.$emit("loading", true);
      try {
        for (let [i, step] of this.settingsLocal.steps.entries()) {
          let prompt = utils.applyTemplate(
            this.settingsLocal.template,
            step.systemMessage ?? "",
            step.userMessage ?? "",
            step.completionInit ?? "",
            prevMessage
          );
          prompt =
            this.mapPrompt && this.mapPrompt[i]
              ? this.mapPrompt[i](prompt)
              : prompt;

          let parameters = this.settingsLocal.modelParameters;
          console.log(prompt);
          answer = await utils.askLLM({
            prompt: prompt,
            ...parameters,
          });
          answer =
            this.mapOutputs && this.mapOutputs[i]
              ? this.mapOutputs[i](answer)
              : answer;
          prevMessage = prompt + answer;
        }
      } catch (e) {
        console.log(e);
        answer = "Error";
      }
      console.log("loading", false);
      this.$emit("loading", false);
      console.log("loading", false);
      this.$emit("update:answer", answer);
    },
  },
  expose: ["sendLLM"],
  data() {
    return {
      enableSendLocal: ref(this.enableSend),
      tab: "Step 1",
      template: ref(""),
      settingsLocal: ref(this.settings),
      modelParameters: {
        max_tokens: {
          placeholder: "Max tokens",
          type: "number",
          model: ref(2048),
        },
        temperature: {
          placeholder: "Temperature",
          type: "float",
          model: ref(0),
        },
        top_p: {
          placeholder: "Top_p",
          type: "float",
          model: ref(null),
        },
        top_k: {
          placeholder: "Top_k",
          type: "number",
          model: ref(null),
        },
        mirostat_tau: {
          placeholder: "Mirostat_tau",
          type: "float",
          model: ref(3.0),
        },
        repetition_penalty: {
          placeholder: "Repetition penalty",
          type: "float",
          model: ref(1.1),
        },
      },
    };
  },
  created() {},
  beforeUpdate() {},
  mounted() {
    this.settingsLocal.template = sanitizeTemplate(this.settingsLocal.template);
  },
};
</script>

<template>
  <div
    class="full-height column justify-between full-width no-wrap overflow-auto"
  >
    <q-list class="full-height column no-wrap" dense>
      <q-item class="q-pa-none flex justify-end" dense>
        <q-btn-dropdown flat icon="more_vert">
          <q-list dense>
            <q-item clickable v-close-popup @click="loadSettings">
              <q-item-section> Load Settings</q-item-section>
            </q-item>

            <q-item clickable v-close-popup @click="saveSettings">
              <q-item-section> Save Settings</q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </q-item>
      <q-expansion-item
        dense
        icon="settings"
        label="Model Settings"
        header-class=""
        :group="accordion ? 'group' : null"
      >
        <q-card class="q-pa-none col">
          <q-card-section
            class="q-pa-sm"
            style="
              display: grid;
              grid-template-columns: 1fr 1fr;
              grid-column-gap: 1em;
            "
          >
            <div
              class="flex col-grow"
              v-for="[key, param] in Object.entries(modelParameters)"
              :key="param"
            >
              <q-input
                :model-value="param.model"
                @update:model-value="updateSetting(key, $event)"
                :type="param.type === 'float' ? 'number' : param.type"
                :step="param.type === 'float' ? '0.01' : ''"
                :label="param.placeholder"
                style="width: 48%; flex-grow: 1"
                class="q-pa-none"
              />
            </div>
          </q-card-section>
        </q-card>
      </q-expansion-item>

      <q-separator />
      <q-expansion-item
        dense
        icon="edit_note"
        label="Template"
        header-class=""
        :group="accordion ? 'group' : null"
      >
        <div class="no-wrap column" style="gap: 10px">
          <div class="row full-width">
            <label class="text-center row items-center justify-start col-4"
              >Assistant Message Start</label
            >
            <q-input
              class="col"
              dense
              :model-value="this.settingsLocal.template?.assistantMessageStart"
              @update:model-value="
                updateTemplate('assistantMessageStart', $event)
              "
            ></q-input>
          </div>
          <div class="row full-width">
            <label class="text-center row items-center justify-start col-4"
              >Assistant Message End</label
            >
            <q-input
              class="col"
              dense
              :model-value="this.settingsLocal.template?.assistantMessageEnd"
              @update:model-value="
                updateTemplate('assistantMessageEnd', $event)
              "
            ></q-input>
          </div>
          <div class="row full-width">
            <label class="text-center row items-center justify-start col-4"
              >System Message Start</label
            >
            <q-input
              class="col"
              dense
              :model-value="this.settingsLocal.template?.systemMessageStart"
              @update:model-value="updateTemplate('systemMessageStart', $event)"
            ></q-input>
          </div>
          <div class="row full-width">
            <label class="text-center row items-center justify-start col-4"
              >System MessageEnd</label
            >
            <q-input
              class="col"
              dense
              :model-value="this.settingsLocal.template?.systemMessageEnd"
              @update:model-value="updateTemplate('systemMessageEnd', $event)"
            ></q-input>
          </div>
          <div class="row full-width">
            <label class="text-center row items-center justify-start col-4"
              >User Message Start</label
            >
            <q-input
              class="col"
              dense
              :model-value="this.settingsLocal.template?.userMessageStart"
              @update:model-value="updateTemplate('userMessageStart', $event)"
            ></q-input>
          </div>
          <div class="row full-width">
            <label class="text-center row items-center justify-start col-4"
              >User Message End</label
            >
            <q-input
              class="col"
              dense
              :model-value="this.settingsLocal.template?.userMessageEnd"
              @update:model-value="updateTemplate('userMessageEnd', $event)"
            ></q-input>
          </div>
        </div>
      </q-expansion-item>
      <q-separator />

      <q-expansion-item
        dense
        icon="edit_note"
        label="Prompt"
        header-class=""
        @show="updateHeights()"
        :group="accordion ? 'group' : null"
      >
        <q-card class="bg-grey-3">
          <q-tabs
            v-model="tab"
            align="left"
            outside-arrows
            class="shadow-2 col"
            @click="updateHeights"
          >
            <q-tab
              class="hover-visible-child full-width"
              @click="updateHeights()"
              v-for="step in settingsLocal.steps"
              :key="step"
              :name="step.name"
              :label="step.name"
            >
              <q-badge
                class="child bg-red q-pa-none"
                style="padding: 0 5% 0 5%"
                @click="removeStep(step.name)"
                floating
              >
                <q-icon name="remove" color="black" />
              </q-badge>
            </q-tab>
            <q-btn @click="addStep()" icon="add" flat></q-btn>
          </q-tabs>
          <q-tab-panels v-model="tab">
            <q-tab-panel
              v-for="step in settingsLocal.steps"
              :key="step"
              :name="step.name"
              class="q-pa-none"
            >
              <prompt-template
                ref="promptTemplate"
                :system-message="step.systemMessage"
                @update:system-message="
                  step.systemMessage = $event;
                  updateSettings();
                "
                :user-message="step.userMessage"
                @update:user-message="
                  step.userMessage = $event;
                  updateSettings();
                "
                :completion-init="step.completionInit"
                @update:completion-init="
                  step.completionInit = $event;
                  updateSettings();
                "
              >
              </prompt-template>
            </q-tab-panel>
          </q-tab-panels>
        </q-card>
        <div class="q-pa-sm flex justify-end full-width">
          <q-btn class="q-mx-sm" flat icon="cleaning_services" />
          <q-btn
            v-show="enableSend"
            class="q-mx-sm bg-primary text-white"
            flat
            label="Send"
            icon-right="send"
            @click="sendLLM()"
          />
        </div>
      </q-expansion-item>

      <q-separator />

      <q-expansion-item
        dense
        icon="output"
        label="Model Output"
        :group="accordion ? 'group' : null"
      >
        <q-card class="bg-grey-3 q-pa-sm full-height">
          <textarea
            ref="answer"
            class="bg-white col q-pa-sm no-border rounded-borders full-width"
            style="
              white-space: pre-line;
              min-height: 10em;
              height: 100%;
              resize: none;
            "
            :value="this.answer"
            @focusin="adjustHeight($event.target)"
            @input="
              $emit('update:answer', $event.target.value);
              adjustHeight($event.target);
            "
          />
        </q-card>
      </q-expansion-item>
      <q-separator />
    </q-list>
  </div>
</template>

<style scoped lang="scss">
.hover-visible-child {
  .child {
    display: none;
  }

  &:hover {
    .child {
      display: block;
    }
  }
}
</style>
