<script setup>
import { ArticleReader } from '@/features/articles/components'
import { onMounted, ref } from "vue";
import { getThePublishedArticle } from "@/features/articles/api";
import { useRoute } from "vue-router";

const route = useRoute();

const title = ref('')
const content = ref({ type: 'doc', content: [] })

onMounted(async () => {
  const response = await getThePublishedArticle(route.params.id)

  title.value = response.data.data.title
  content.value = response.data.data.content

  console.log("load article successfully")
})

</script>

<template>

  <div class="col-body-container items-center">
    <ArticleReader
        v-if="title && content"
        :title="title"
        :content="content"
    />
  </div>
</template>
