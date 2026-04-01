<script setup>
import { useUserStore } from "@/features/user/stores";
import { computed } from "vue";
import { useRouter, useRoute } from 'vue-router'

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const userInfo = computed(() => userStore.userInfo);
const avatarUrl = computed(() => import.meta.env.VITE_API_BASE_URL + userStore.userInfo?.avatar)

function updateUrl(patch = {}) {
  const merged = { ...route.query, ...patch }

  // Delete fields with values ''/undefined/null
  Object.keys(merged).forEach((k) => {
    if (merged[k] === undefined || merged[k] === null || merged[k] === '') {
      delete merged[k]
    }
  })

  router.replace({
    name: 'my-articles',
    query: merged,
  })
}
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

    <!-- Filters -->
    <div class="flex flex-col gap-y-3">
      <p class="font-bold text-[20px]">Filters</p>

      <!-- Status Filter -->
      <div class="flex flex-col gap-2 w-full h-auto max-w-full min-w-0">
        <p class="font-bold text-[15px]">Status</p>

        <div class="flex flex-wrap gap-2 w-full max-w-full min-w-0">

          <div
              class="article-sidebar-filter-query"
              @click="updateUrl({ article_status: undefined })">
            <p class="text-[12px] font-bold">All</p>
          </div>
          <div
              class="article-sidebar-filter-query"
              @click="updateUrl({ article_status: '0' })">
            <p class="text-[12px] font-bold">Draft</p>
          </div>
          <div
              class="article-sidebar-filter-query"
              @click="updateUrl({ article_status: '1' })">
            <p class="text-[12px] font-bold">Pending</p>
          </div>
          <div
              class="article-sidebar-filter-query"
              @click="updateUrl({ article_status: '2' })">
            <p class="text-[12px] font-bold">Published</p>
          </div>
          <div
              class="article-sidebar-filter-query"
              @click="updateUrl({ article_status: '3' })">
            <p class="text-[12px] font-bold">Rejected</p>
          </div>
          <div
              class="article-sidebar-filter-query"
              @click="updateUrl({ article_status: '4' })">
            <p class="text-[12px] font-bold">Unpublished</p>
          </div>

        </div>

      </div>
    </div>

  </div>
</template>