<script>
import { ref } from "vue";

export default {
  name: "ResizableDrawer",
  data() {
    return {
      draggable: false,
      resizableWidth: ref(30),
    };
  },
  methods: {
    startDrag() {
      this.draggable = true;
      this.$refs.resizableBlock.addEventListener("mousemove", this.handleDrag);
      this.$refs.resizableBlock.addEventListener("mouseup", this.stopDrag);
    },

    handleDrag(event) {
      if (this.draggable) {
        const draggableWidth =
          event.clientX -
          this.$refs.resizableBlock.getBoundingClientRect().left;
        const blockWidth = this.$refs.resizableBlock.offsetWidth;
        let newResizable1Width = Math.min(
          Math.max((draggableWidth / blockWidth) * 100, 30),
          70
        );
        this.resizableWidth = newResizable1Width.toFixed(2);
      }
    },
    stopDrag() {
      this.draggable = false;
      this.$refs.resizableBlock.removeEventListener(
        "mousemove",
        this.handleDrag
      );
      this.$refs.resizableBlock.removeEventListener("mouseup", this.stopDrag);
    },
  },
};
</script>

<template>
  <div class="full-height full-width row" ref="resizableBlock">
    <div class="full-height" :style="{ width: resizableWidth + '%' }">
      <slot name="block1"></slot>
    </div>
    <div
      style="
        cursor: col-resize;
        background-color: #b9b9b9;
        width: 2px;
        margin: 0 8px;
      "
      class="full-height"
      @mousedown="startDrag(this.$refs.resizableBlock)"
    ></div>
    <div
      class="full-height"
      :style="{ width: 'calc(100% - 18px - ' + resizableWidth + '%' }"
    >
      <slot name="block2"></slot>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
