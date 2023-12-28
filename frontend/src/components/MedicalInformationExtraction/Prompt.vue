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
  exposes: ['run'],
  emits: ['askLLM', 'clearOutput'],

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
      const parameters = Object.fromEntries(Object.entries(this.modelParameters).map(([key, value]) => [key, value.model]));
      this.$emit('askLLM', {prompt: prompt, parameters: parameters});
    },

  },
  data(){

    return{
      modelParameters: {
        max_tokens: {
          placeholder: "Max tokens",
          type: "number",
          model: ref(2048),
        },
        temperature: {
          placeholder: "Temperature",
          type: "float",
          model: ref(0.5),
        },
        // top_p: {
        //   placeholder: "Top_p",
        //   type: "float",
        //   model: ref(0),
        // },
        // top_k: {
        //   placeholder: "Top_k",
        //   type: "number",
        //   model: ref(0),
        // },
        mirostat_tau: {
          placeholder: "Mirostat_tau",
          type: "float",
          model: ref(8.0),
        },
        repeat_penalty: {
          placeholder: "Repeat penalty",
          type: "float",
          model: ref(1.1),
        }
      },

      completionInit: ref(this.promptCompletionInit),
      userMessage: ref(this.promptUserMessage),
      systemMessage: ref(this.promptSystemMessage),

    }
  },
  mounted() {
    this.adjustHeight(this.$refs.systemMessage);
    this.adjustHeight(this.$refs.prompt);
    this.adjustHeight(this.$refs.completionInit);
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
          <q-card-section class="q-pa-sm flex justify-start">
            <q-input
              v-for="param in modelParameters" :key="param"
              v-model="param.model"
              :type="param.type === 'float' ? 'number' : param.type"
              :step="param.type === 'float' ? '0.01' : ''"
              :label="param.placeholder"
              style="width: 48%"
              class="q-pa-none"
            />
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
                <q-btn class="q-mx-sm" round dense flat icon="send" @click="prepareData()"/>
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
        <q-card>
          <q-card-section style="white-space: pre-line">
            {{ answer }}
          </q-card-section>
        </q-card>
      </q-expansion-item>
      <q-separator/>

    </q-list>
  </div>


</template>

<style scoped lang="sass">

</style>
