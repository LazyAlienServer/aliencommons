<script setup>
import { useRouter } from "vue-router";
import { computed } from 'vue';

const router = useRouter();

const props = defineProps({
  article: {
    type: Object,
    required: true,
  }
})

const to = computed(() => {
  const status = props.article.status
  console.log(props.article)

  // Pending
  if (status === 1) {
    return { name: 'article-review', params: { id: props.article.id } }
  }

  // Published
  if (status === 2) {
    return { name: 'article-detail', params: { id: props.article.published_version_id } }
  }

  return { name: 'article-editor', params: { id: props.article.id } }
})
</script>

<template>
  <div class="article-card">
    <!-- Title and Status-->
    <div class="flex flex-row items-center gap-2">

      <router-link
          :to="to"
          class="text-lg font-semibold truncate hover:text-blue-500 hover:underline transition"
      >
        {{ article?.title }}
      </router-link>

      <div class="border border-gray-300 rounded-full flex flex-col py-0.5 px-2 items-center">
        <span class="text-[12px] font-bold text-gray-600 ">{{ article?.status_display }}</span>
      </div>

    </div>

    <!-- Meta -->

    <span>
      Created:
      {{ new Date(article?.created_at).toLocaleString() }}
    </span>

    <span>
      Updated:
      {{ new Date(article?.updated_at).toLocaleString() }}
    </span>

  </div>
</template>
