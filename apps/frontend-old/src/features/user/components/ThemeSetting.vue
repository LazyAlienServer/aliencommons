<script setup>
import { useThemeStore } from "@/features/user/stores";

const themeStore = useThemeStore();

function applyTheme(mode) {
  themeStore.applyTheme(mode);
}
</script>

<template>
  <div class="flex flex-col gap-y-5 mt-6 w-full">
    <p class="text-[25px]">
      Theme preferences
    </p>

    <hr class="w-full">

    <div class="flex flex-row gap-x-20">

      <div class="flex flex-col items-center gap-y-5 p-5 rounded-md hover-auto" @click="applyTheme('light')">
        <div class="w-75 h-45 bg-light border-1 border-gray-500 rounded-md flex flex-col items-center justify-center">
          <p class="text-light mr-1">This is a line.</p>
        </div>
        <p class="mr-1">Light Default</p>
      </div>

      <div class="flex flex-col items-center gap-y-5 p-5 rounded-md hover-auto" @click="applyTheme('dark')">
        <div class="w-75 h-45 bg-dark border-1 border-gray-500 rounded-md flex flex-col items-center justify-center">
          <p class="text-dark mr-1">This is a line.</p>
        </div>
        <p class="mr-1">Dark Default</p>
      </div>

    </div>

  </div>
</template>