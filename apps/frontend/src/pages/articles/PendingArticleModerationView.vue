<script setup>
import { ArticleReader, ModerationToolBar } from '@/features/articles/components'
import { onMounted, ref } from "vue";
import { getThePendingArticle, approveArticle, rejectArticle } from "@/features/articles/api";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "vue-toastification";

const route = useRoute();
const router = useRouter();
const toast = useToast();

const title = ref('')
const content = ref({ type: 'doc', content: [] })
const articleId = ref(null)

onMounted(async () => {
  const response = await getThePendingArticle(route.params.id)

  title.value = response.data.data.title
  content.value = response.data.data.content
  articleId.value = response.data.data.article_id
})

const loading = ref(false);

async function handleApprove() {
  loading.value = true;

  try {
    await approveArticle(articleId.value);
    toast.success("Article approved successfully!");
    await router.push({ name: 'pending-articles' });

  } catch (error) {
    toast.error(error.response?.data?.message);
    console.error("Failed to approve the article", error);

  } finally {
    loading.value = false;
  }
}

async function handleReject() {
  loading.value = true;

  try {
    await rejectArticle(articleId.value);
    toast.success("Article rejected successfully!");
    await router.push({ name: 'pending-articles' });

  } catch (error) {
    toast.error(error.response?.data?.message);
    console.error("Failed to reject the article", error);

  } finally {
    loading.value = false;
  }
}
</script>

<template>

  <Teleport to="#page-header">
    <ModerationToolBar
        :loading="loading"
        @approve="handleApprove()"
        @reject="handleReject()"
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
