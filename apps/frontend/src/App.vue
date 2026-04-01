<script setup>
import { AppHeader, AppFooter, PageHeader } from "@/components/layout";
import { computed } from 'vue'
import { useRoute } from "vue-router";

const route = useRoute();

const showPageHeader = computed(() => {
  const last = route.matched[route.matched.length - 1]
  return last?.meta?.showPageHeader === true
})
</script>

<template>
  <div class="flex flex-col min-h-screen font-sans text-light dark:text-dark backgrounds-auto">
    <AppHeader />
    <PageHeader v-if="showPageHeader"/>

    <main
        class="flex-1 flex flex-col"
        :class="showPageHeader ? 'pt-38': 'pt-28'"
    >
      <router-view />
    </main>

    <AppFooter />

  </div>
</template>

<style>
</style>
