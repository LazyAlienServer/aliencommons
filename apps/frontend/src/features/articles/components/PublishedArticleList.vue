<script setup>
import { ref, onMounted } from "vue";
import { getPublishedArticles } from "@/features/articles/api";
import { PublishedArticleInfoCard } from "@/features/articles/components";

const publishedArticles = ref([])

onMounted(async() => {
  const response = await getPublishedArticles()
  publishedArticles.value = response.data.results
  console.log("Load published articles successfully!")
})
</script>

<template>
  <div class="flex flex-col gap-y-4 w-full h-135 overflow-y-auto">

    <PublishedArticleInfoCard
        v-for="publishedArticle in publishedArticles"
        :key="publishedArticle.id"
        :published-article="publishedArticle"
    />

  </div>
</template>
