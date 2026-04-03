<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { ArticleEditor } from '@/features/articles/components'

const isDirty = ref(false)
const isHydrating = ref(true)

function beforeUnloadHandler(event) {
  if (!isDirty.value) return
  event.preventDefault()
  event.returnValue = ''
}

onMounted(() => {
  window.addEventListener('beforeunload', beforeUnloadHandler)
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', beforeUnloadHandler)
})

onBeforeRouteLeave(() => {
  if (!isDirty.value) return true
  return window.confirm('Changes will not be saved. Leave this page?')
})

function handleEditorUpdate() {
  if (isHydrating.value) return
  isDirty.value = true
}

function handleHydrationDone() {
  isHydrating.value = false
}

async function handleSaved() {
  isDirty.value = false
}
</script>

<template>
  <div class="col-body-container items-center">
    <ArticleEditor
        @update="handleEditorUpdate"
        @hydration-done="handleHydrationDone"
        @saved="handleSaved"
        :is-dirty="isDirty"
    />
  </div>
</template>
