<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
        <q-toolbar-title class="column" style="text-align:center">
          <div>
            HBD-Demo
          </div>
          <div style="font-size:small;">
            Health Big Data Project, Working Group 1: Text Analysis
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
