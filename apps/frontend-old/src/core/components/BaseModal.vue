<script setup>
import { watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits(['update:modelValue'])

function close() {
  emit('update:modelValue', false)
}

function lockBody() {
  document.body.style.overflow = 'hidden'
}

function unlockBody() {
  document.body.style.overflow = ''
}

watch(
    () => props.modelValue,
    (isOpen) => {
      if (isOpen) {
        lockBody()
      } else {
        unlockBody()
      }
    },
    { immediate: true }
)

function handleKeydown(e) {
  if (!props.modelValue) return
  if (e.key === 'Escape') {
    close()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  unlockBody()
})
</script>

<template>
  <Teleport to="body">
    <div
        v-if="modelValue"
        class="modal"
    >
      <!-- Mask -->
      <div
          class="modal-mask"
          @click="close()"
      />

      <!-- Modal content -->
      <div
          class="modal-content"
          @click.stop
      >
        <slot />
      </div>
    </div>
  </Teleport>
</template>