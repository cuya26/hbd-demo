<template>
    <q-card>
        <q-card-section class=" row justify-between" >
            <div class="col-2"></div>
            <div class="text-h6 text-primary">Output</div>
            <div class="col-2" v-if="!deidentified"></div>
            <div v-if="deidentified" class="col-2 justify-end row">
                <q-btn label="Reset" class="text-primary" flat rounded dense @click="deidentified=false" />
            </div>
        </q-card-section>
        <q-card-section>
            <div v-if="!deidentified" class="q-pl-sm q-pt-sm column justify-begin no-wrap" style="height:100%">
            <div class=" q-pb-md row justify-evenly">
                <q-btn
                style="width: 100px"
                dense
                :disable="inputLetter===null"
                label="de-identify"
                rounded
                :loading="loading"
                color="primary"
                @click="deidentify()"
            />
            </div>

            <div class="q-pl-md q-py-md column">
                <div class="">Select the entities that you want to de-identify:</div>
                <div class="row justify-start q-pb-sm" v-for="entityType in Object.keys(deidentificationConf)" :key="entityType">
                <q-checkbox
                v-model="deidentificationConf[entityType].show"
                style="width: 150px"
                :color="deidentificationConf[entityType].color"
                :label="deidentificationConf[entityType].name"
                @update:model-value="value => resetDeidModel(value, entityType)"
                />

                <q-select
                v-if="deidentificationConf[entityType].show"
                v-model="deidentificationConf[entityType].value"
                :options="deidentificationConf[entityType].options"
                dense
                outlined
                style="width: 170px"
                />
                </div>
                <!-- <q-checkbox v-model="deidentificationDict['Codice Fiscale']" false-value="" true-value="select model" color="red-6" label="Codice Fiscale" /> -->
            </div>

            <div class="q-pl-md" v-if="deidentificationConf.date?deidentificationConf['date'].show:false">
                <q-select
                v-model="dateAnonymLevel"
                :options="optionsDateAnonymLevel"
                dense
                outlined
                label="Select level of date anonymization"
                style="width: 300px"
                />
            </div>
            </div>
            <div v-show="deidentified" ref="deidentifiedTextDiv"  class="q-pa-md q-m" style="white-space: pre-line; max-height: 560px; min-height: 560px ;overflow:auto; border: 1px solid rgba(0, 0, 0, 0.24);border-radius: 4px;">
            ""
            </div>
        </q-card-section>
    </q-card>
</template>

<script>
import {defineComponent, ref} from "vue";
import {api} from "boot/axios";

export default defineComponent ({
    name: "DeidentificationClassic",
    props:  ['inputLetter'],  
    setup () {
        return {
            loading: ref(false),
            deidentified: ref(false),
            deidentificationConf: ref({
            'person': {
                show: true,
                color: 'pink-5',
                options: [
                'spacy', 'stanza'
                ],
                value: 'stanza',
                default: 'stanza',
                name: 'Person Name'
            },
            'fiscal_code': {
                show: true,
                color: 'red-4',
            options: [
                'regex'
                ],
                value: 'regex',
                default: 'regex',
                name: ' Fiscal Code'
            },
            'email': {
                show: true,
                color: 'indigo-5',
            options: [
                'regex'
                ],
                value: 'regex',
                default: 'regex',
                name: 'Email'
            },
            'telephone': {
                show: true,
                color: 'yellow-5',
            options: [
                'regex'
                ],
                value: 'regex',
                default: 'regex',
                name: 'Telephone'
            },
            'address': {
                show: true,
                color: 'orange-5',
            options: [
                'spacy', 'stanza'
                ],
                value: 'stanza',
                default: 'stanza',
                name: 'Address'
            },
            'zipcode': {
                show: true,
                color: 'brown-5',
            options: [
                'regex'
                ],
                value: 'regex',
                default: 'regex',
                name: 'Zip Code'
            },
            'age': {
                show: true,
                color: 'purple-5',
            options: [
                'regex'
                ],
                value: 'regex',
                default: 'regex',
                name: 'Age'
            },
            'organization': {
                show: true,
                color: 'teal-5',
            options: [
                'spacy', 'stanza'
                ],
                value: 'stanza',
                default: 'stanza',
                name: 'Organization',
            },
            'date': {
                show: true,
                color: 'green-5',
            options: [
                'regex'
                ],
                value: 'regex',
                default: 'regex',
                name: 'Date'
            },
            }),
            dateAnonymLevel: ref('hide date'),
            optionsDateAnonymLevel: ref([
                'hide date',
                'Keep only the year',
                'keep only month'
            ]),
            dictDateAnonymLevel: ref({
                'hide date': 'hide',
                'Keep only the year': 'year',
                'keep only month': 'month'
            }),
        }
    },
    methods: {
        deidentify () {
            this.loading = true

            let deidentificationModelDict = {}
            for ( const [entityType, entityTypeDict] of Object.entries(this.deidentificationConf)) {
                if ( this.deidentificationConf[entityType] ) {
                deidentificationModelDict[entityType] = this.deidentificationConf[entityType].value
                } else {
                deidentificationModelDict[entityType] = ''
                }
            }
            console.log(deidentificationModelDict)
            api.post(
                '/deidentify',
                {
                cfg: {
                models: deidentificationModelDict,
                mask: {
                    mode: "tag",
                    special_character: "*",
                    date_level: this.dictDateAnonymLevel[this.dateAnonymLevel]
                }
                },
                input_text: this.inputLetter
            }).then( (response) => {
                let deidentifiedText = response.data['deidentified_text']
                this.$refs.deidentifiedTextDiv.innerHTML = this.highlight(deidentifiedText)
                // this.deidentifiedText = this.deidentifiedText.replace(/<DATA>/, '<span class="bg-primary"><DATA></span>')
                this.deidentified = true
                this.loading = false
            }).catch( (error) => {
                this.loading=false
                console.log('ops an error occurs')
                error.message
            })
        },
        highlight (text) {

            text = text.replace(/</g, '&lt').replace(/>/g, '&gt')

            text = text.replace(/&ltTELEFONO&gt/g, '<span class="bg-yellow-3">&ltTELEFONO&gt</span>')
            text = text.replace(/&ltCAP&gt/g, '<span class="bg-brown-3">&ltCAP&gt</span>')
            text = text.replace(/&ltE-MAIL&gt/g, '<span class="bg-indigo-3">&ltE-MAIL&gt</span>')
            text = text.replace(/&ltPERSONA&gt/g, '<span class="bg-pink-3">&ltPERSONA&gt</span>')
            text = text.replace(/&ltORGANIZZAZIONE&gt/g, '<span class="bg-teal-3">&ltORGANIZZAZIONE&gt</span>')
            text = text.replace(/&ltINDIRIZZO&gt/g, '<span class="bg-orange-3">&ltINDIRIZZO&gt</span>')
            text = text.replace(/&ltDATA&gt/g, '<span class="bg-green-3">&ltDATA&gt</span>')
            text = text.replace(/&ltCF&gt/g, '<span class="bg-red-4">&ltCF&gt</span>')
            text = text.replace(/&ltETÀ&gt/g, '<span class="bg-purple-4">&ltETÀ&gt</span>')

            // this.$refs.deidentifiedTextDiv.$el
            // this.$refs.deidentifiedTextDiv.replace(/prova/, '<span>prova</span>')
            // this.$refs.deidentifiedTextDiv.innerHTML = this.$refs.deidentifiedTextDiv.innerHTML.replace(/<DATA>/, '<span>####</span>')
            return text
        },
        resetDeidModel(value, entityType) {
            if (value === true ) this.deidentificationConf[this.setupName][entityType].value = this.deidentificationConf[this.setupName][entityType].default
            if (value === false) this.deidentificationConf[this.setupName][entityType].value = ''
        },
    }
})
</script>