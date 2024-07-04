<script>
import { ref } from "vue";

export default {
  name: "ResizableDrawer",
  data() {
    return {
      isResizing: false,
      resizableWidth: ref(30),
    };
  },
};
</script>

<template>
  <div class="">
    <div>
      <slot name="block1"></slot>
    </div>
    <div>
      <slot name="block2"></slot>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
