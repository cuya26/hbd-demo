<script>
import { ref } from "vue";
import { sendMessageToLLM } from "components/MedicalInformationExtraction/utils";

export default {
  name: "MIEChat",
  props: { doc: String },
  mounted() {
    setTimeout(() =>{

      this.chat[0].content = this.systemMessage.replace("{doc}", this.doc??'');

    }, 10)
  },
  data() {
    return {
      text: ref(""),
      dense: true,
      loading: ref(false),
      systemMessage: ref(`
Questa è una conversazione tra un utente umano e un assistente artificiale esperto di medicina.
L'assistente è empatico ed educato.
L'assistente parla in italiano e risponde alle domande in italiano.
L'assistente è qui per rispondere alle domande, fornire consigli e aiutare l'utente a prendere decisioni.
L'assistente è tenuto a rispondere a domande o task riguardanti i testi clinici al meglio delle sue possibilità.
Le risposte sono coincise ed esaustive.

--- CONTESTO ---
{doc}
----------------
      `),
      chat: ref([
        {
          role: "system",
          content: "",
        },
      ]),
    };
  },
  watch: {
    doc: function (newValue) {
      this.chat[0].content = this.systemMessage.replace("{doc}", newValue??'');
    },
  },
  methods: {
    clear(){
      this.chat = [this.chat[0]]
    },
    send() {
      this.chat.push({
        content: this.text,
        role: "user",
      });
      this.chat.push({
        role: "assistant",
        content: "",
      });

      sendMessageToLLM(this.chat, {})
        .then((response) => {
          this.text = ""
        let reader = response.getReader();
        const processStream = ({ done, value }) => {
          if (done) {
            this.loading = false;
            return;
          }
          let chunkRaw = new TextDecoder().decode(value);
          const chunkArray = chunkRaw.split("data:").slice(1);

          for (let chunk of chunkArray) {
            try {
              chunk = JSON.parse(chunk.split(": ping -")[0]);
            } catch {
              console.log("il parsing non è andato a buon fine");
              console.log(chunk);
            }
            if (Object.keys(chunk).includes("choices")) {
              if (Object.keys(chunk["choices"][0]["delta"]).includes("role")) {
                this.chat.slice(-1)[0]["role"] =
                  chunk["choices"][0]["delta"]["role"];
                this.chat.slice(-1)[0]["content"] = "";
              } else {
                this.chat.slice(-1)[0]["content"] += chunk["choices"][0][
                  "delta"
                ]["content"]
                  ? chunk["choices"][0]["delta"]["content"]
                  : "";
                // Gestisci il chunk di evento ricevuto dallo stream
                this.$nextTick(() => {
                  this.$refs.chatWindow.scrollTop =
                    this.$refs.chatWindow.scrollHeight;
                });
              }
            }
          }
          return reader.read().then(processStream);
        };
        reader.read().then(processStream);
      })
    },
  },
};
</script>

<template>
  <div class="column full-height full-width q-pa-sm overflow-auto">
    <q-expansion-item
      expand-separator
      label="Context"
      header-class="bg-primary text-white full-width"
      expand-icon-class="text-white"
    >
      <q-card class="overflow-auto" style="max-height: 400px; width: 100%">
        <q-card-section>
          <div style="white-space: break-spaces">
            {{ this.chat[0].content }}
          </div>
        </q-card-section>
      </q-card>
    </q-expansion-item>
    <div class="scrollbar-hidden q-pa-md row justify-center col">
      <div
        style="width: 100%; overflow: scroll"
        class="scrollbar-hidden full-height"
        ref="chatWindow"
      >
        <q-chat-message
          v-for="message in chat"
          v-show="message.role !== 'system'"
          :key="message"
          :text="[message.content]"
          :sent="message.role === 'user'"
        />
      </div>
    </div>
    <div class="col-grow">
      <div class="col-grow"></div>
    </div>
    <q-input bottom-slots v-on:keyup.enter="send"  v-model="text" label="Message" :dense="dense">
      <template v-slot:after>
        <q-btn
          round
          dense
          flat
          icon="delete"
          @click="clear()"
        />
        <q-btn
          :disable="text.trim() === ''"
          round
          dense
          flat
          icon="send"
          @click="send"
        />
      </template>
    </q-input>
  </div>
</template>

<style scoped lang="scss">
.scrollbar-hidden::-webkit-scrollbar {
  display: none;
}

/* Hide scrollbar for IE, Edge add Firefox */
.scrollbar-hidden {
  -ms-overflow-style: none;
  scrollbar-width: none; /* Firefox */
}
</style>
