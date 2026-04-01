<script setup>
import { ref, watch } from "vue";
import { getMySourceArticles } from "@/features/articles/api";
import { MyArticleInfoCard } from "@/features/articles/components";
import { useRoute } from 'vue-router'

const route = useRoute();

const articles = ref([])

async function fetchArticles(query) {
  try {
    const response = await getMySourceArticles(query)
    articles.value = response.data.results
    console.log("Load articles successfully!")
  } catch (error) {
    console.log("Load articles failed", error)
  }
}

watch(
    () => route.query,
    (newQuery) => {
      fetchArticles(newQuery)
    },
    { deep: true, immediate: true }
)
</script>

<template>
  <div class="flex flex-col w-full gap-y-3">

    <p class="h-15 text-[25px] font-bold shrink-0">My Articles</p>

    <div class="flex flex-col gap-y-4 h-125 overflow-y-auto pr-10">

      <MyArticleInfoCard
          v-for="article in articles"
          :key="article.id"
          :article="article"
      />

    </div>
  </div>
</template>
