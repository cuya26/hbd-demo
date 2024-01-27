<script>
export default {
  name: "InformationSourceLocalization",
  data() {
    return {};
  },
  mounted() {
    setTimeout(() => {
      this.$refs.text.innerHTML = this.text;
    });
  },
  methods: {
    highlightLine(props) {
      let rowIndex = props.rowIndex;
      let lines = this.rows[rowIndex].lines;
      if (lines.length > 1) {
        lines = [...Array(lines[1] - lines[0] + 1).keys()].map(
          (i) => i + lines[0]
        );
      }
      let highlightedText = this.text.split("\n");
      lines.forEach((line) => {
        highlightedText[
          line
        ] = `<span highlight="true">${highlightedText[line]}</span>`;
      });
      this.$refs.text.innerHTML = highlightedText.join("\n");
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
      this.$emit("ok");
      // or with payload: this.$emit('ok', { ... })

      // then hiding dialog
      this.hide();
    },

    onCancelClick() {
      // we just need to hide the dialog
      this.hide();
    },
  },

  props: {
    rows: [],
    columns: [],
    text: String,
  },

  emits: [
    // REQUIRED
    "ok",
    "hide",
  ],
};
</script>

<template>
  <q-dialog class="full-width full-height" ref="dialog" @hide="onDialogHide">
    <q-card
      class="q-dialog-plugin full-width full-height q-pa-md column"
      style="max-width: unset; gap: 10px"
    >
      <div class="flex col" style="gap: 10px">
        <q-card bordered class="full-height bg-grey-2 col rounded-borders">
          <div
            style="white-space: pre-line; overflow: scroll; height: 100%"
            ref="text"
          ></div>
        </q-card>
        <q-card bordered class="bg-grey-2 col">
          <q-table
            class="col col-grow"
            title="Medications"
            :rows="rows"
            :columns="columns"
            row-key="name"
            :rows-per-page-options="[0, 10, 20, 30]"
          >
            <template v-slot:body="props">
              <q-tr :props="props" @mouseenter="highlightLine(props)">
                <q-td key="name" :props="props">
                  {{ props.row.name }}
                </q-td>
                <q-td key="dose" :props="props">
                  {{ props.row.dose }}
                </q-td>
                <q-td key="frequency" :props="props">
                  {{ props.row.frequency }}
                </q-td>
                <q-td key="route" :props="props">
                  {{ props.row.route }}
                </q-td>
                <q-td key="lines" :props="props">
                  {{ props.row.lines }}
                </q-td>
              </q-tr>
            </template>
          </q-table>
        </q-card>
      </div>
      <q-card-actions align="right">
        <q-btn color="primary" label="OK" @click="onOKClick" />
        <q-btn color="primary" label="Cancel" @click="onCancelClick" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<style lang="scss">
span[highlight="true"] {
  background-color: rgba(116, 198, 232, 0.4);
}
</style>
