<script>
import { ref } from "vue";

export default {
  name: "PromptComponent",
  expose: ["updateHeights"],
  props: {
    template: String,
    answer: String,
    systemMessage: String,
    userMessage: String,
    completionInit: String,
    accordion: Boolean,
    modelSettings: {
      type: Object,
      default: undefined,
    },
    enableSend: {
      type: Boolean,
      default: true,
    },

    enableAnswer: {
      type: Boolean,
      default: true,
    },
  },
  watch: {
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
  exposes: ["prepareDate"],
  emits: [
    "update:systemMessage",
    "update:userMessage",
    "update:completionInit",
    "update:answer",
    "update:modelSettings",
    "update:template",
    "askLLM",
    "clearOutput",
  ],

  methods: {
    updateHeights() {
      this.adjustHeight(this.$refs.systemMessage);
      this.adjustHeight(this.$refs.userMessage);
      this.adjustHeight(this.$refs.completionInit);
      this.adjustHeight(this.$refs.answer);
    },
    adjustHeight(element) {
      if (!element) return;
      element.style.height = 0 + "px";
      element.style.height = element.scrollHeight + "px";
    },
    askLLM() {
      this.$emit("askLLM");
    },
    updateSetting(key, value) {
      this.modelParameters[key].model = value;
      this.modelParameters[key].enabled = true;
    },
    emitModelSettings() {
      let modelSettings = Object.fromEntries(
        Object.entries(this.modelParameters).map(([key, value]) => [
          key,
          value.model,
        ])
      );
      this.$emit("update:modelSettings", modelSettings);
    },
  },

  data() {
    return {
      templates: [
        `<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
{prompt}<|im_end|>
<|im_start|>assistant
{completion_init}`,
        `[INST]
{system_message}

{prompt}
[/INST]
{completion_init}
`,
        `{system_message} USER: {prompt} ASSISTANT: {completion_init}`,
      ],
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
  mounted() {
    this.adjustHeight(this.$refs.systemMessage);
    this.adjustHeight(this.$refs.userMessage);
    this.adjustHeight(this.$refs.completionInit);
    this.adjustHeight(this.$refs.answer);

    if (this.modelSettings !== undefined) {
      for (const [key, value] of Object.entries(this.modelSettings)) {
        if (value) this.updateSetting(key, value);
      }
    }
  },
};
</script>

<template>
  <div
    class="full-height column justify-between full-width no-wrap overflow-auto"
  >
    <q-list class="full-height column no-wrap">
      <q-expansion-item
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
                @update:model-value="
                  updateSetting(key, $event);
                  emitModelSettings();
                "
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
        icon="edit_note"
        label="Template"
        header-class=""
        :group="accordion ? 'group' : null"
      >
        <div class="flex no-wrap" style="gap: 10px">
          <div
            v-for="(template, index) in templates"
            :key="template"
            class="q-pa-sm flex"
          >
            <q-checkbox
              style="align-items: start !important"
              class="flex column items-start q-pa-md"
              :model-value="template === this.template"
              @update:model-value="
                console.log(template);
                $emit('update:template', template);
              "
            >
              <template v-slot:default>
                <div style="white-space: pre-line">
                  {{ template }}
                </div>
              </template>
            </q-checkbox>
            <q-separator vertical v-if="index < templates.length - 1" />
          </div>
        </div>
      </q-expansion-item>
      <q-separator />

      <q-expansion-item
        icon="edit_note"
        label="Prompt"
        header-class=""
        :group="accordion ? 'group' : null"
        default-opened
      >
        <q-card>
          <div class="bg-grey-3 overflow-scroll column full-height">
            <div
              class="col-grow flex q-pa-sm justify-end bg-grey-4 full-height"
            >
              <div style="display: flex">
                <q-btn
                  class="q-mx-sm"
                  v-if="enableAnswer"
                  round
                  dense
                  flat
                  icon="cleaning_services"
                  @click="$emit('clearOutput')"
                />
                <q-btn
                  v-if="enableSend"
                  class="q-mx-sm"
                  round
                  dense
                  flat
                  icon="send"
                  @click="askLLM()"
                />
              </div>
            </div>

            <div class="q-pa-sm col overflow-auto flex column">
              <p style="margin: 0">System Message:</p>
              <textarea
                class="bg-white q-pa-sm no-border rounded-borders full-width"
                style="resize: none"
                ref="systemMessage"
                placeholder="System message"
                :value="this.systemMessage"
                @focusin="adjustHeight($event.target)"
                @input="
                  $emit('update:systemMessage', $event.target.value);
                  adjustHeight($event.target);
                "
              />
              <p style="margin: 0">User Message:</p>

              <textarea
                placeholder="User message"
                class="bg-white q-pa-sm no-border rounded-borders full-width"
                style="resize: none"
                ref="userMessage"
                :value="this.userMessage"
                @focusin="adjustHeight($event.target)"
                @input="
                  $emit('update:userMessage', $event.target.value);
                  adjustHeight($event.target);
                "
              ></textarea>

              <p style="margin: 0">Completion Init</p>
              <textarea
                contenteditable="true"
                class="bg-white q-pa-sm no-border rounded-borders full-width"
                style="resize: none"
                ref="completionInit"
                placeholder="Completion init"
                @focusin="adjustHeight($event.target)"
                :value="this.completionInit"
                @input="
                  $emit('update:completionInit', $event.target.value);
                  adjustHeight($event.target);
                "
              />
            </div>
          </div>
        </q-card>
      </q-expansion-item>

      <q-separator />

      <q-expansion-item
        v-if="enableAnswer"
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

<style scoped lang="sass"></style>
