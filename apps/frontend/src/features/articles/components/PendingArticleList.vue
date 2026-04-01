<script setup>
import { ref, onMounted } from "vue";
import { getPendingArticles } from "@/features/articles/api";
import { PendingArticleInfoCard } from "@/features/articles/components";

const pendingArticles = ref([])

onMounted(async() => {
  const response = await getPendingArticles()
  pendingArticles.value = response.data.data
  console.log("Load pending articles successfully!")
})
</script>

<template>
  <div class="flex flex-col gap-y-4 w-full h-135 overflow-y-auto">

    <PendingArticleInfoCard
        v-for="pendingArticle in pendingArticles"
        :key="pendingArticle.id"
        :pending-article="pendingArticle"
    />

  </div>
</template>
