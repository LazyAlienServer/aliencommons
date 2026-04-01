<script setup>
import { ArticleReader, ReviewToolBar } from '@/features/articles/components'
import { onMounted, ref } from "vue";
import { getTheSourceArticle, withdrawArticle } from "@/features/articles/api";
import { useRoute } from "vue-router";

const route = useRoute();

const title = ref('')
const content = ref({ type: 'doc', content: [] })

onMounted(async () => {
  const response = await getTheSourceArticle(route.params.id)

  title.value = response.data.data.title
  content.value = response.data.data.content
})

const loading = ref(false);

async function handleWithdraw() {
  loading.value = true;
  const id = route.params.id

  try {
    await withdrawArticle(id);
    toast.success("Article withdrew successfully!");
    await router.push({ name: 'article-editor', params: { id }});

  } catch (error) {
    toast.error(error.response?.data?.message);
    console.error("Failed to withdraw the article", error);

  } finally {
    loading.value = false;
  }
}
</script>

<template>

  <Teleport to="#page-header">
    <ReviewToolBar
        :loading="loading"
        @withdraw="handleWithdraw()"
    />
  </Teleport>

  <div class="col-body-container items-center">
    <ArticleReader
        v-if="title && content"
        :title="title"
        :content="content"
    />
  </div>
</template>