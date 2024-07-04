<template>
    <q-card>
        <q-card-section class=" row justify-between" >
            <div class="col-2"></div>
            <div class="text-h6 text-primary">Output</div>
            <div class="col-2"></div>
        </q-card-section>
    
        <q-card-section
        class="" style="height: 90%"
        >
            <div style="width: 100%;" class="q-pa-sm">
              <div class="row no-wrap" style="width: 100%;">
                <q-input
                  style="width: 100%"
                  rounded
                  outlined
                  dense
                  v-model="patientSearchText"
                  placeholder="Write a condition"
                  @keyup.enter="searchPatient"
                />
                <div class="q-px-sm"></div>
                <q-btn
                  :loading="loadingPatientSearch"
                  round
                  color="primary"
                  icon="search"
                  @click="searchPatient"
                />
              </div>
              <div class="q-pt-md">
                <q-table
                  class="my-sticky-virtscroll-table"
                  :rows-per-page-options="[0]"
                  table-header-style="text-align: left"
                  table-header-class="align-left text-primary text-bold"
                  wrap-cells
                  dense
                  separator="cell"
                  :visible-columns="visiblePatientColumns"
                  :columns="patientColumns"
                  :rows="patientResults"
                  :loading="loadingPatientSearch"
                >
                  <template v-slot:loading>
                    <q-inner-loading showing color="primary" />
                  </template>
                  <template v-slot:body-cell="props">
                    <q-td :props="props">
                        <span style="cursor: pointer" @click="showRetrievedDocument(props.row.text)">{{ props.value }}</span>
                    </q-td>
                  </template>
                </q-table>
              </div>
            </div>
        </q-card-section>
    </q-card>
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
import {patientSearchApi} from "boot/axios";

const patientColumns = [
{ name: 'document_id', label: 'id', field: 'document_id', required: true, sortable: false, align: 'left'},
{ name: 'context', label: 'context', field: 'context', required: true, sortable: false, align: 'left'},
{ name: 'text', label: 'text', field: 'text', required: false, sortable: false, align: 'left'}
]

const visiblePatientColumns = [
  'document_id',
  'context'
]

export default defineComponent({
    name: 'PatientSearch',
    props:  [
        'inputLetter',
        'inputMode'
    ],
    emits:['update:inputMode', 'update:inputLetter'],
    data () {
        return {
            visiblePatientColumns,
            patientColumns,
            loadingPatientSearch: ref(false),
            patientSearchText: ref(''),
            patientResults: ref([]),
        }
    },
    methods: {
        searchPatient () {
            this.loadingPatientSearch = true
            patientSearchApi.post(
                '/patient_search',
                { query: this.patientSearchText}
            ).then( (response) => {
                console.log(response.data)
                this.loadingPatientSearch = false
                this.patientResults = response.data.output
            }).catch( (error) => {
                error.message
                console.log('error with patient search call')
                this.loadingPatientSearch = false
            })
            },
            showRetrievedDocument (text) {
            this.$emit('update:inputLetter', text);
            this.$emit('update:inputMode', "edit")
            this.dropzoneURL = ''
        }
    }
})
</script>