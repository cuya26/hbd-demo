<template>
    <q-card class="" >
        <q-card-section class=" row justify-between" >
            <div class="col-2"></div>
            <div class="text-h6 text-primary">Output</div>
            <div class="col-2"></div>
        </q-card-section>
        <q-card-section>
            <div class="q-px-md q-pb-md row justify-evenly">
                <q-btn @click="extractValues" rounded color="primary" label="Compute" :disable="inputLetter===null"/>
            </div>
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
            :visible-columns="visibleColumns"
            :rows="medicationList"
            :loading="loading"
            >
                <template v-slot:loading>
                    <q-inner-loading showing color="primary" />
                </template>
                <template v-slot:body-cell="props">
                    <q-td :props="props">
                        <span style="cursor: pointer" @click="loadSaliencyMapDrugExtraction(props.row.sentence, props.value, props.col.name)">{{ props.value }}</span>
                    </q-td>
                </template>
            </q-table>
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
import {defineComponent, ref} from "vue";
import {api} from "boot/axios";

const columns = [
  { name: 'drug', label: 'Farmaco', field: 'entity', required: true, sortable: true, align: 'left'},
  { name: 'sentence', label: 'Sentence', field: 'sentence', required: false, sortable: false, align: 'left'},
  { name: 'disposition', label: 'Evento', field: 'disposition', required: true, sortable: true, align: 'left' },
  { name: 'action', label: 'Azione', field: 'Action', required: true, sortable: true, align: 'left' },
  { name: 'negation', label: 'Negazione', field: 'Negation', required: true, sortable: true, align: 'left' },
  { name: 'temporality', label: 'Tempo', field: 'Temporality', required: true, sortable: true, align: 'left' },
  { name: 'actor', label: 'Attuatore', field: 'Actor', required: true, sortable: true, align: 'left' },
  { name: 'certainty', label: 'Certezza', field: 'Certainty', required: true, sortable: true, align: 'left' }
]

const visibleColumns = [
'drug',
'disposition',
'action',
'negation',
'temporality',
'actor',
'certainty',
]

export default defineComponent ({
    name: "PharmacologicalEventExtraction",
    props:  [
        'inputLetter',
        'modelConfig',
        'inputMode',
        'saliencyMap',
        'loadingSaliencyMap'
        
    ],
    emits:['update:inputMode', 'update:saliencyMap'],
    setup () {
        return {
            loading: ref(false),
            medicationList: ref([]),
            columns,
            visibleColumns
        }
    },
    methods: {
        extractValues () {
            this.loading=true
            api.post(
                '/extract_data_table',
                { input_text: this.inputLetter}
            ).then( (response) => {
                this.loading=false
                console.log(response.data)
                this.medicationList = response.data
            }).catch((error)=>{
                this.loading=false
                console.log('ops an error occurs')
                error.message
            })
            },
            loadSaliencyMapDrugExtraction (sentence, target, colName) {
                this.$emit('update:saliencyMap', []);
                console.log(this.modelConfig)
                console.log(colName)
                this.$emit('update:loadingSaliencyMap', true);
                api.post(
                '/compute_saliency_map',
                {
                    task_type: 'drug_event_extraction',
                    task: colName,
                    input_text: this.inputLetter,
                    sentence: sentence,
                    target_text: target,
                    model_type: this.modelConfig[colName].modelType,
                    model_name: this.modelConfig[colName].modelName,
                    model_lang: this.modelConfig[colName].lang,
                },
                { timeout: 360000 }
                ).then ( (response) => {
                    this.$emit('update:loadingSaliencyMap', false);
                    this.$emit('update:inputMode', "saliency");
                    this.$emit('update:saliencyMap', response.data.saliency_map);
                }).catch( (error) =>{
                    this.$emit('update:loadingSaliencyMap', false);
                    console.log('ops an error occurs during the computing of the saliency maps')
                    error.message
                })
            },
    }
})
</script>