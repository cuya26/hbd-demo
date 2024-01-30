<script>
import { ref } from "vue";
import MedicationExtraction from "components/MedicalInformationExtraction/MedicationExtraction.vue";
import TimelineExtraction from "components/MedicalInformationExtraction/TimelineExtraction.vue";
import { config } from "components/MedicalInformationExtraction/utils";

/* @formatter:on */
export default {
  name: "MedicalInformationExtraction",

  components: { TimelineExtraction, MedicationExtraction },
  props: ["doc"],

  mounted() {
    // this.openInformationSourceLocalization();
  },
  data() {
    return {
      page: ref("Medication Extraction"),
      mini: ref(true),
      config: ref(config),
      searchServer: ref(""),
    };
  },
  methods: {},
};
</script>

<template>
  <div class="full-height">
    <q-layout view="hHh Lpr lff" container class="shadow-2 rounded-borders">
      <q-header elevated class="bg-primary">
        <q-toolbar>
          <q-btn flat @click="mini = !mini" round dense icon="menu" />
          <q-toolbar-title>{{ page }}</q-toolbar-title>
        </q-toolbar>
      </q-header>

      <q-drawer
        :model-value="true"
        show-if-above
        :mini="mini"
        :width="300"
        :breakpoint="500"
        bordered
        class="bg-grey-3"
      >
        <q-scroll-area class="fit" :horizontal-thumb-style="{ opacity: 0 }">
          <q-list padding>
            <q-item
              :active="page === 'Medication Extraction'"
              clickable
              v-ripple
              @click="page = 'Medication Extraction'"
            >
              <q-item-section avatar>
                <q-icon name="medication" />
              </q-item-section>

              <q-item-section> Medication Extraction</q-item-section>
            </q-item>

            <q-item
              :active="page === 'Timeline extraction'"
              clickable
              v-ripple
              @click="page = 'Timeline extraction'"
            >
              <q-item-section avatar>
                <q-icon name="timeline" />
              </q-item-section>

              <q-item-section> Timeline Extraction</q-item-section>
            </q-item>

            <q-item
              :active="page === 'Settings'"
              clickable
              v-ripple
              @click="page = 'Settings'"
            >
              <q-item-section avatar>
                <q-icon name="settings" />
              </q-item-section>

              <q-item-section> Settings</q-item-section>
            </q-item>
          </q-list>
        </q-scroll-area>
      </q-drawer>

      <q-page-container>
        <q-page v-if="page === 'Medication Extraction'" padding>
          <medication-extraction :doc="doc"></medication-extraction>
        </q-page>
        <q-page v-if="page === 'Timeline extraction'" padding>
          <timeline-extraction :doc="doc"></timeline-extraction>
        </q-page>
        <q-page
          v-if="page === 'Settings'"
          style="gap: 20px"
          class="full-width flex column"
          padding
        >
          <span class="full-width text-center text-h6"> Settings </span>
          <div style="width: 50%">
            <q-list
              bordered
              separator
              class="overflow-auto"
              style="max-height: 300px"
            >
              <q-item
                :active="config.selectedServer.url === server.url"
                v-for="server in config.servers"
                :key="server"
                clickable
                v-ripple
                @click="config.selectedServer = server"
              >
                <q-item-section>
                  <q-item-label title>{{ server.name }}</q-item-label>
                  <q-item-label caption>{{ server.url }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
            <q-input
              v-if="config.servers.length > 10"
              v-model="searchServer"
              label="Search Server"
            />
          </div>

          <div class="flex items-center">
            <label>LLama.cpp api</label>
            <q-toggle
              v-model="config.OpenAI_API"
              color="primary"
              label="OpenAI API"
            />
          </div>
        </q-page>
      </q-page-container>
    </q-layout>
  </div>
</template>

<style scoped lang="scss">
::-webkit-scrollbar {
  display: none;
}
</style>
