<script setup>
const props = defineProps({
  pendingArticle: {
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
          :to="{ name: 'article-moderation', params: { id: pendingArticle.id } }"
          class="text-lg font-semibold truncate hover:text-blue-500 hover:underline transition"
      >
        {{ pendingArticle?.title }}
      </router-link>

    </div>

    <!-- Meta -->

    <span>
      Created:
      {{ new Date(pendingArticle?.created_at).toLocaleString() }}
    </span>

  </div>
</template>
