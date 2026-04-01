<script setup>
import { useUserStore } from "@/features/user/stores";
import { computed } from "vue";

const userStore = useUserStore();
const userInfo = computed(() => userStore.userInfo);
const avatarUrl = computed(() => import.meta.env.VITE_API_BASE_URL + userStore.userInfo?.avatar)
</script>

<template>
  <div class="flex flex-col gap-2 mr-15 h-auto gap-y-10 w-1/5">

    <!-- Avatar and Info -->
    <div class="flex flex-row items-center gap-3">

      <img
          :src="avatarUrl"
          alt="User Avatar"
          class="w-13 h-13 rounded-full object-cover border border-gray-300"
      />

      <div class="flex flex-col mb-0.5">
        <p class="text-[22px] font-semibold">{{ userInfo?.username }}</p>
        <p class="text-[12px] ml-0.5 text-gray-600">{{ userInfo?.email }}</p>
      </div>

    </div>


  </div>
</template>