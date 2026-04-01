<script setup>
const props = defineProps({
  publishedArticle: {
    type: Object,
    required: true,
  }
})
</script>

<template>
  <div class="article-card">
    <!-- Title and Status-->
    <div class="flex flex-row items-center gap-2">

      <router-link
          :to="{ name: 'article-detail', params: { id: publishedArticle.id } }"
          class="text-lg font-semibold truncate hover:text-blue-500 hover:underline transition"
      >
        {{ publishedArticle?.title }}
      </router-link>

    </div>

    <!-- Meta -->
    <span>
      Created:
      {{ new Date(publishedArticle?.created_at).toLocaleString() }}
    </span>

  </div>
</template>
