<script setup lang="ts">
const themeStore = useThemeStore();

function applyTheme(mode) {
  themeStore.applyTheme(mode);
}
</script>

<template>
  <div class="mt-6 flex w-full flex-col gap-y-5">
    <p class="text-[25px]">Theme preferences</p>

    <hr class="w-full" />

    <div class="flex flex-row gap-x-20">
      <div
        class="hover-auto flex flex-col items-center gap-y-5 rounded-md p-5"
        @click="applyTheme('light')"
      >
        <div
          class="flex h-45 w-75 flex-col items-center justify-center rounded-md border-1 border-gray-500 bg-light"
        >
          <p class="mr-1 text-light">This is a line.</p>
        </div>
        <p class="mr-1">Light Default</p>
      </div>

      <div
        class="hover-auto flex flex-col items-center gap-y-5 rounded-md p-5"
        @click="applyTheme('dark')"
      >
        <div
          class="flex h-45 w-75 flex-col items-center justify-center rounded-md border-1 border-gray-500 bg-dark"
        >
          <p class="mr-1 text-dark">This is a line.</p>
        </div>
        <p class="mr-1">Dark Default</p>
      </div>
    </div>
  </div>
</template>
