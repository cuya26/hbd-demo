<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
        <q-toolbar-title style="text-align:center">
          HBD-Demo
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
