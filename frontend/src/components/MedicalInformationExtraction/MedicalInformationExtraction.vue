<script>
import { ref } from "vue";
import MedicationExtraction from "components/MedicalInformationExtraction/MedicationExtraction.vue";
import TimelineExtraction from "components/MedicalInformationExtraction/TimelineExtraction.vue";
import {
  config,
  saveServer,
} from "components/MedicalInformationExtraction/utils";

/* @formatter:on */
export default {
  name: "MedicalInformationExtraction",

  components: { TimelineExtraction, MedicationExtraction },
  props: ["doc"],

  mounted() {
  },
  data() {
    return {
      page: ref("Medication Extraction"),
      mini: ref(true),
      config: ref(config),
      searchServer: ref(""),
    };
  },
  methods: {
    saveServer,
  },
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
        <q-page v-show="page === 'Medication Extraction'" padding>
          <medication-extraction
            :doc="doc"
            :show="page === 'Medication Extraction'"
          ></medication-extraction>
        </q-page>
        <q-page v-show="page === 'Timeline extraction'" padding>
          <timeline-extraction
            :doc="doc"
            :show="page === 'Timeline extraction'"
          ></timeline-extraction>
        </q-page>
        <q-page
          v-show="page === 'Settings'"
          style="gap: 20px"
          class="full-width flex column"
          padding
        >
          <span class="full-width text-center text-h6"> Settings </span>
          <div style="width: 100%">
            <q-list
              bordered
              separator
              class="overflow-auto"
              style="max-height: 400px"
            >
              <q-item
                :active="config.selectedServer.url === server.url"
                v-for="server in config.servers"
                :key="server"
                clickable
                v-ripple
                @click="
                  config.selectedServer = server;
                  console.log(config.selectedServer);
                "
              >
                <q-item-section>
                  <q-item-label title>{{ server.name }}</q-item-label>
                  <q-item-label caption>{{ server.url }}</q-item-label>
                </q-item-section>
                <q-item-section avatar>
                  <div class="flex items-center">
                    <label>LLama.cpp api</label>
                    <q-toggle
                      v-model="server.OpenAI_API"
                      color="primary"
                      label="OpenAI API"
                    />
                  </div>
                </q-item-section>
              </q-item>
            </q-list>
            <div class="flex column bg-grey-3 q-pa-sm">
              <div class="flex no-wrap justify-between items-center">
                <div class="flex" style="gap: 10px">
                  <q-input
                    v-model="config.customServer.name"
                    label="Add Server Name"
                  />
                  <q-input
                    v-model="config.customServer.url"
                    label="Add Server Url"
                  />
                  <div class="flex items-center">
                    <label>LLama.cpp api</label>
                    <q-toggle
                      @update:model-value="
                        config.customServer.OpenAI_API =
                          !config.customServer.OpenAI_API;
                      "
                      :model-value="config.customServer.OpenAI_API"
                      color="primary"
                      label="OpenAI API"
                    />
                  </div>
                </div>
              </div>
              <div class="full-width flex justify-end" style="gap: 10px">
                <q-btn
                  color="primary"
                  :disable="
                    config.customServer.url === '' ||
                    config.customServer.name === ''
                  "
                  label="Save"
                  @click="saveServer()"
                />
              </div>
            </div>

            <q-input
              v-if="config.servers.length > 10"
              v-model="searchServer"
              label="Search Server"
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
