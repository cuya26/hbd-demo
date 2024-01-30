<script>
import * as axios from "boot/axios";

export default {
  name: "TasksDialog",
  props: {
    tasks: Array,
    taskName: String,
    onSetTask: Function,
    save: Boolean,
  },
  mounted() {
    this.loadProperties();
  },
  watch: {
    taskName() {
      this.loadProperties();
    },
  },

  emits: [
    // REQUIRED
    "ok",
    "hide",
  ],
  data() {
    return {
      taskProperties: "",
      overwrite: false,
    };
  },
  methods: {
    loadProperties() {
      axios.api
        .get(`/get_properties/${this.taskName}`)
        .then((res) => {
          this.overwrite = true;
          let obj = JSON.parse(res.data);
          res = JSON.stringify(obj, null, 4);
          this.taskProperties = res;
        })
        .catch(() => {
          this.overwrite = false;
          this.taskProperties = "";
        });
    },
    setTaskName(taskName) {
      console.log(taskName);
      this.onSetTask(taskName);
    },

    // following method is REQUIRED
    // (don't change its name --> "show")
    show() {
      this.$refs.dialog.show();
    },

    // following method is REQUIRED
    // (don't change its name --> "hide")
    hide() {
      this.$refs.dialog.hide();
    },

    onDialogHide() {
      // required to be emitted
      // when QDialog emits "hide" event
      this.$emit("hide");
    },

    onOKClick() {
      // on OK, it is REQUIRED to
      // emit "ok" event (with optional payload)
      // before hiding the QDialog
      this.$emit("ok", this.taskName);
      // or with payload: this.$emit('ok', { ... })

      // then hiding dialog
      this.hide();
    },

    onCancelClick() {
      // we just need to hide the dialog
      this.hide();
    },
  },
};
</script>

<template>
  <q-dialog
    ref="dialog"
    @hide="onDialogHide"
    style="width: 100%; max-width: unset"
  >
    <q-card
      class="q-dialog-plugin column no-wrap justify-between"
      style="max-width: unset; width: 70%; height: 60%"
    >
      <div class="flex no-wrap" style="height: 80%">
        <div style="width: 35%; height: 100%">
          <q-card-section>
            <q-item-label header class="text-h5">
              <q-icon name="info" />
              <span class="q-ml-sm">Save Settings</span>
            </q-item-label>
          </q-card-section>
          <q-item-label>
            <span class="q-ml-lg text-h6">Saved Tasks</span>
          </q-item-label>
          <q-card-section style="height: 70%" class="overflow-auto">
            <q-list bordered separator>
              <q-item
                :active="task === taskName"
                v-for="task in tasks"
                :key="task"
                clickable
                v-ripple
                @click="setTaskName(task)"
              >
                {{ task }}
              </q-item>
            </q-list>
          </q-card-section>
        </div>
        <q-separator vertical />
        <q-input
          :model-value="taskProperties"
          autogrow
          readonly
          filled
          type="textarea"
          style="width: 65%; height: 100%"
          class="overflow-auto taskProperties q-pa-md rounded-borders"
        />
      </div>

      <q-card-actions
        align="right"
        style="height: 19%"
        class="full-width q-pa-lg"
      >
        <q-input
          v-if="save"
          class="col q-px-lg"
          :model-value="taskName"
          @update:model-value="setTaskName($event)"
          label="Task Name"
          error-message="Task properties will be overwritten"
          :error="overwrite"
        />
        <q-btn color="primary" label="Cancel" @click="onCancelClick" />
        <q-btn
          color="primary"
          :label="save ? 'Save' : 'Load'"
          @click="onOKClick"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<style lang="scss">
.taskProperties {
  white-space: pre-line;
}
</style>
