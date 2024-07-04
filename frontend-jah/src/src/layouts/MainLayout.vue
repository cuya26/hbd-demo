<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
        <!-- <img src="quasar-logo-vertical.svg"/> -->
        <q-toolbar-title class="row justify-between" style="text-align:center">
        <div class="column justify-evenly">
          <img src="../assets/XAI_lab_logo.png" style="width: 210px;"/>
        </div>
        <div>
          <div>
            XAI-Demo
          </div>
          <div style="font-size:small;">
            Health Big Data Project, Working Group 1: Text Analysis
          </div>
        </div>
        <div class="column justify-evenly">
          <img src="../assets/Logo_polimi.png" style="width: 200px;"/>
        </div>
        </q-toolbar-title>
    </q-header>

     <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>


<script>
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'MainLayout',

  setup () {

    return {
    }
  }
})
</script>
