<script setup>
import { BookDown } from "lucide-vue-next";

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
        @click="$emit('withdraw')"
    >
      <BookDown size="21"/>
      <span class="editor-toolbar-btn-tooltip">Withdraw article</span>
    </button>

  </div>
</template>
