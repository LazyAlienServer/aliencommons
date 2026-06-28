<script setup lang="ts">
import { PaintBrushIcon } from "~/assets/icons";
import { computed } from "vue";
import { RouterLink } from "vue-router";

const userStore = useUserStore();
const userInfo = computed(() => userStore.userInfo);
const avatarUrl = computed(
  () => import.meta.env.VITE_API_BASE_URL + userStore.userInfo?.avatar
);
</script>

<template>
  <div class="mr-15 flex h-auto w-1/5 flex-col gap-2 gap-y-6">
    <div class="flex flex-row items-center gap-3">
      <img
        :src="avatarUrl"
        alt="User Avatar"
        class="h-13 w-13 rounded-full border border-gray-300 object-cover"
      />

      <div class="mb-0.5 flex flex-col">
        <p class="text-[22px] font-semibold">{{ userInfo?.username }}</p>
        <p class="ml-0.5 text-[12px] text-gray-600">{{ userInfo?.email }}</p>
      </div>
    </div>

    <div class="flex flex-col gap-y-3">
      <router-link :to="{ name: 'appearance' }" class="sidebar-link">
        <PaintBrushIcon class="sidebar-icon" />
        Appearance
      </router-link>
    </div>
  </div>
</template>
