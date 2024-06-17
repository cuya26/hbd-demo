<script>
import { ref } from "vue";

export default {
  name: "MIEChat",
  props: { doc: String },
  data() {
    return {
      text: ref(""),
      dense: true,
      chat: ref([
        {
          text: "cioa",
          sender: "bot",
        },
        {
          text: "sdfsd",
          sender: "user",
        },
        {
          text: "sdfsd",
          sender: "user",
        },
      ]),
    };
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
          {{ doc }}
        </q-card-section>
      </q-card>
    </q-expansion-item>
    <div class="q-pa-md row justify-center">
      <div style="width: 100%; max-width: 400px">
        <q-chat-message
          v-for="message in chat"
          :key="message"
          :text="[message.text]"
          :sent="message.sender === 'user'"
        />
      </div>
    </div>
    <div class="col-grow">
      <div class="col-grow"></div>
    </div>
    <q-input
      bottom-slots
      v-model="text"
      label="Label"
      counter
      maxlength="12"
      :dense="dense"
    >
      <template v-slot:append>
        <q-icon
          v-if="text !== ''"
          name="close"
          @click="text = ''"
          class="cursor-pointer"
        />
        <q-icon name="schedule" />
      </template>

      <template v-slot:hint> Field hint </template>

      <template v-slot:after>
        <q-btn round dense flat icon="send" />
      </template>
    </q-input>
  </div>
</template>

<style scoped lang="scss"></style>
