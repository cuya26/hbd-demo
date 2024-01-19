<script>
import {ref} from "vue";


export default {
  name: "PromptComponent",
  props: {
    template: String,
    answer: String,
    promptSystemMessage: String,
    promptUserMessage: String,
    promptCompletionInit: String,
    accordion: Boolean,
  },
  watch: {
    answer: function (newVal, oldVal) {
      this.internalAnswer = newVal;
      setTimeout(() => {
        this.adjustHeight(this.$refs.answer);
      }, 0);

    },
  },
  exposes: ['prepareDate'],
  emits: ['askLLM', 'clearOutput', 'answerChanged'],

  methods: {
    adjustHeight(element) {
      if (!element) return;
      element.style.height = 0 + 'px';
      element.style.height = element.scrollHeight + "px";
    },

    prepareData() {
      let prompt = this.template
        .replace('{system_message}', this.systemMessage)
        .replace('{prompt}', this.userMessage)
        .replace('{completion_init}', this.completionInit);
      const parameters = Object.fromEntries(Object.entries(this.modelParameters)
        .filter(([key, value]) => value.enabled)
        .map(([key, value]) => [key, value.model]));
      return {prompt: prompt, parameters: parameters};
    },
    askLLM() {
      let data = this.prepareData()
      this.$emit('askLLM', data);
    },
    updateAnswer(text) {
      console.log('update answer')
      this.internalAnswer = text;
      this.$emit('answerChanged', text);
    }

  },
  data() {
    return {
      modelParameters: {
        max_tokens: {
          placeholder: "Max tokens",
          type: "number",
          model: ref(2048),
          enabled: ref(true)
        },
        temperature: {
          placeholder: "Temperature",
          type: "float",
          model: ref(0),
          enabled: ref(true)
        },
        top_p: {
          placeholder: "Top_p",
          type: "float",
          model: ref(0),
          enabled: ref(false)
        },
        top_k: {
          placeholder: "Top_k",
          type: "number",
          model: ref(0),
          enabled: ref(false)
        },
        mirostat_tau: {
          placeholder: "Mirostat_tau",
          type: "float",
          model: ref(3.0),
          enabled: ref(true)

        },
        repeat_penalty: {
          placeholder: "Repeat penalty",
          type: "float",
          model: ref(1.1),
          enabled: ref(false)
        }
      },

      completionInit: ref(this.promptCompletionInit),
      userMessage: ref(this.promptUserMessage),
      systemMessage: ref(this.promptSystemMessage),
      internalAnswer: ref(this.answer),
    }
  },
  mounted() {
    this.adjustHeight(this.$refs.systemMessage);
    this.adjustHeight(this.$refs.prompt);
    this.adjustHeight(this.$refs.completionInit);
    this.adjustHeight(this.$refs.answer);

  },

}
</script>

<template>
  <div class="full-height column justify-between full-width no-wrap overflow-auto">
    <q-list class="full-height column no-wrap">
      <q-expansion-item
        icon="settings"
        label="Model Settings"
        header-class=""
        :group="accordion ? 'group' : null"
      >
        <q-card class="q-pa-none col">
          <q-card-section class="q-pa-sm" style="display: grid; grid-template-columns: 1fr 1fr; grid-column-gap: 1em">
            <div class="flex col-grow"
                 v-for="param in modelParameters" :key="param"
            >
              <q-checkbox v-model="param.enabled"></q-checkbox>
              <q-input
                :disable="!param.enabled"
                v-model="param.model"
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

      <q-separator/>

      <q-expansion-item
        icon="edit_note"
        label="Prompt"
        header-class=""
        :group="accordion ? 'group' : null"

        default-opened>
        <q-card>
          <div class="bg-grey-3 overflow-scroll column full-height">
            <div class="col-grow flex q-pa-sm justify-end bg-grey-4 full-height">
              <div style="display: flex;">
                <q-btn class="q-mx-sm" round dense flat icon="cleaning_services" @click="$emit('clearOutput')"/>
                <q-btn class="q-mx-sm" round dense flat icon="send" @click="askLLM()"/>
              </div>
            </div>

            <div class="q-pa-sm col overflow-auto flex column">
              <p style="margin: 0">
                {{ this.template.slice(0, this.template.indexOf('{system_message}') - 1) }}</p>
              <textarea class="bg-white col q-pa-sm no-border rounded-borders full-width"
                        style="resize: none"
                        ref="systemMessage"
                        placeholder="System message"
                        v-model="this.systemMessage"
              />
              <p style="margin: 0"
                 v-html="this.template.slice(this.template.indexOf('{system_message}')+16, this.template.indexOf('{prompt}')-1)
                                  .replace('\n', '<br>')"></p>

              <div class="col-grow">
                <textarea placeholder="User message"
                          class="q-pa-sm no-border rounded-borders full-width bg-white"
                          style="resize: none"
                          ref="prompt"
                          v-model="this.userMessage"
                          @input="adjustHeight($event.target)"
                ></textarea>
              </div>

              <p style="margin: 0"
                 v-html="this.template.slice(this.template.indexOf('{prompt}')+8, this.template.indexOf('{completion_init}')-1)
                                  .replace('\n', '<br>')"
              ></p>
              <textarea contenteditable="true" class="bg-white col q-pa-sm no-border rounded-borders full-width"
                        style="resize: none"
                        ref="completionInit"
                        placeholder="Completion init"
                        v-model="this.completionInit"
                        @input="adjustHeight($event.target)"
              />
            </div>
          </div>

        </q-card>
      </q-expansion-item>


      <q-separator/>

      <q-expansion-item
        icon="output"
        label="Model Output"
        :group="accordion ? 'group' : null"

      >
        <q-card class="bg-grey-3 q-pa-sm full-height">
          <textarea
            ref="answer"
            class="bg-white col q-pa-sm no-border rounded-borders full-width"
            style="white-space: pre-line; min-height: 10em; height: 100%; resize: none" v-model="this.internalAnswer"
            @input="adjustHeight($event.target); updateAnswer($event.target.value)"
          />

        </q-card>
      </q-expansion-item>
      <q-separator/>

    </q-list>
  </div>


</template>

<style scoped lang="sass">

</style>
