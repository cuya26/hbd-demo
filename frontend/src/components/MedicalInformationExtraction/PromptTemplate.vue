<script>
export default {
  name: "PromptTemplate",
  props: {
    systemMessage: String,
    userMessage: String,
    completionInit: String,
  },
  methods: {
    updateHeights() {
      setTimeout(() => {
        this.adjustHeight(this.$refs.systemMessage);
        this.adjustHeight(this.$refs.userMessage);
        this.adjustHeight(this.$refs.completionInit);
      });
    },
    adjustHeight(element) {
      if (!element) return;
      element.style.height = 0 + "px";
      element.style.height = element.scrollHeight + "px";
    },
  },
  emits: [
    "update:systemMessage",
    "update:userMessage",
    "update:completionInit",
  ],
  expose: ["updateHeights"],
};
</script>

<template>
  <div class="bg-grey-3 overflow-scroll column full-height">
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
</template>

<style scoped lang="scss"></style>
