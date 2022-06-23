<template>
  <q-page padding class="row items-strech">
    <div class="col-12 column q-pt-xl no-wrap">
      <div class="row no-wrap justify-between" style="height: 100%">
        <q-card class="col-7 items-strech" style="height: 600px">
          <div class="col-12 column no-wrap" style="height: 100%">
            <q-card-section class="row justify-evenly">
            
              <div class="text-h6 text-primary">Discharge Letter</div>
            </q-card-section>
            <q-card-section style="max-height: 90%">
              
              <div style="overflow: auto; flex-grow: 1;max-height: 100%">
                <div class="text-grey-7" style="white-space: pre-line">{{letterList[0]}}</div>
              </div>
            </q-card-section>
          </div>
        </q-card>
        <div class="column justify-evenly">
          <q-btn
          rounded
          label="go!"
          class="bg-primary text-white"
          @click="extractValues"
          />
        </div>
        <q-card class="col-4" style="height: 600px">
          <q-card-section class="row justify-evenly">
            <div class="text-h6 text-primary">Extracted Data</div>
          </q-card-section>
          <q-card-section class="q-pa-md">
            <q-table
              class="my-sticky-virtscroll-table"
              :rows-per-page-options="[0]"
              table-header-style="text-align: left"
              table-header-class="align-left text-primary text-bold"
              wrap-cells
              hide-bottom
              dense
              virtual-scroll
              :virtual-scroll-item-size="48"
              :virtual-scroll-sticky-size-start="48"
              separator="cell"
              :columns="columns"
              :rows="medicationList"
            />
            <!-- <div class="q-pl-sm"  v-for="medication in medicationList" :key="medication">
              <div class="text-primary">{{medication}}</div>
            </div> -->
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<style lang="sass">
.my-sticky-virtscroll-table
  /* height or max-height is important */
  height: 500px

  .q-table__top,
  .q-table__bottom,
  thead tr:first-child th /* bg color is important for th; just specify one */
    background-color: #fff

  thead tr th
    position: sticky
    z-index: 1
  /* this will be the loading indicator */
  thead tr:last-child th
    /* height of all previous header rows */
    top: 48px
  thead tr:first-child th
    top: 0
</style>

<script>
import { defineComponent, ref } from 'vue'
import { api } from 'boot/axios'

const columns = [
  { name: 'drug', label: 'Drug', field: row =>row, required: true, sortable: true, align: 'left'},
  { name: 'disposition', label: 'Disposition', field: row => 'not available', required: true, sortable: true, align: 'left' },
  { name: 'action', label: 'Action', field: row => 'not available', required: true, sortable: true, align: 'left' },
  { name: 'negation', label: 'Negation', field: row => 'not available', required: true, sortable: true, align: 'left' },
  { name: 'temporality', label: 'Temporality', field: row => 'not available', required: true, sortable: true, align: 'left' },
  { name: 'actor', label: 'Actor', field: row => 'not available', required: true, sortable: true, align: 'left' },
  { name: 'certainty', label: 'Certainty', field: row => 'not available', required: true, sortable: true, align: 'left' }
]

export default defineComponent({
  name: 'IndexPage',
  setup () {
    return {
      letterList: ref([]),
      medicationList: ref([]),
      columns
    }
  },
  methods : {
    extractValues () {
      api.post(
        '/extract_data_table',
        { input_text: this.letterList[0]}
      ).then( (response) => {
        console.log(response.data)
        this.medicationList = response.data
      })
    }
  },
  created () {
    api.get(
      '/discharge_letters'
    ).then( (response)=> {
      console.log(response.data)
      this.letterList = response.data
    })
  }
})
</script>
