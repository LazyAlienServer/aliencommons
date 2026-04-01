<script setup>
import { Check, X } from "lucide-vue-next";

const props = defineProps({
  loading: {
    type: Boolean,
    default: false,
    required: true
  },
})
</script>

<template>
  <div class="flex flex-row justify-center gap-2 items-center w-1/7 flex-1">
    <button
        type="button"
        class="editor-actions-btn group"
        :disabled="loading"
        @click="$emit('approve')"
    >
      <Check size="21"/>
      <span class="editor-toolbar-btn-tooltip">Approve article</span>
    </button>

    <button
        type="button"
        class="editor-actions-btn group"
        :disabled="loading"
        @click="$emit('reject')"
    >
      <X size="21"/>
      <span class="editor-toolbar-btn-tooltip">Reject article</span>
    </button>

  </div>
</template>
