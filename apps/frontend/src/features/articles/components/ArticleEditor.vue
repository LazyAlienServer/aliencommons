<script setup>
import { useEditor, EditorContent } from '@tiptap/vue-3'
import { StarterKit } from '@tiptap/starter-kit'
import { Highlight } from "@tiptap/extension-highlight";
import { Superscript } from '@tiptap/extension-superscript';
import { Subscript } from '@tiptap/extension-subscript';
import { TextAlign } from '@tiptap/extension-text-align';
import { Mathematics } from '@tiptap/extension-mathematics';
import { TaskItem, TaskList } from '@tiptap/extension-list';
import { Placeholder, CharacterCount } from '@tiptap/extensions';
import { Image } from '@tiptap/extension-image';
import { FileHandler } from '@tiptap/extension-file-handler';
import { Youtube } from '@tiptap/extension-youtube';
import { useRoute, useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { onMounted, ref } from "vue";
import { getTheSourceArticle, submitArticle, updateSourceArticle, deleteArticle } from "@/features/articles/api";
import { EditorToolBar } from "@/features/articles/components";
import { uploadArticleImage } from '@/features/articles/api'

const route = useRoute();
const router = useRouter();
const toast = useToast();

const id = ref(null)
const title = ref(null)
const content = ref(null)

const props = defineProps({
  isDirty: {
    type: Boolean,
    required: true,
  }
})

async function handleImageUpload(editor, files) {
  for (const file of files) {
    if (!file.type.startsWith('image/')) continue

    const MAX = 4 * 1024 * 1024
    if (file.size > MAX) {
      toast.error('Image upload failed')
      continue
    }

    const formData = new FormData()
    formData.append('image', file)

    try {
      const response = await uploadArticleImage(formData)
      const url = response.data.data.url
      const imageUrl =  import.meta.env.VITE_API_BASE_URL + url

      editor.chain().focus().setImage({ src: imageUrl, alt: file.name }).run()

    } catch (error) {
      console.log('Image upload failed')
      toast.error('Image upload failed')
    }
  }
}

const title_editor = useEditor({
  content: '',
  onUpdate: () => emit('update'),
  extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder: 'What is your title?',
      }),
      CharacterCount,
  ],
})

const content_editor = useEditor({
  content: '',
  onUpdate: () => emit('update'),
  extensions: [
      StarterKit.configure({
        link: {
          openOnClick: true,
          autolink: true,
          defaultProtocol: 'https',
          linkOnPaste: true,
          HTMLAttributes: {
            class: 'link',
            rel: 'noopener noreferrer',
            target: '_blank',
          },
        },
        heading: {
          levels: [1, 2, 3],
        },
      }),
      TaskList,
      TaskItem.configure({
        nested: false,
      }),
      Superscript,
      Subscript,
      Highlight,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
        defaultAlignment: 'left',
      }),
      Mathematics.configure({
        blockOptions: {
          onClick: (node, pos) => {
            const newCalculation = prompt('Enter new calculation:', node.attrs.latex)
            if (newCalculation) {
              const editor = content_editor.value
              editor.chain().setNodeSelection(pos).updateBlockMath({ latex: newCalculation }).focus().run()
            }
          },
        },
        inlineOptions: {
          onClick: (node, pos) => {
            const editor = content_editor.value
            const newCalculation = prompt('Enter new calculation:', node.attrs.latex)
            if (newCalculation) {
              editor.chain().setNodeSelection(pos).updateInlineMath({ latex: newCalculation }).focus().run()
            }
          },
        },
      }),
      Placeholder.configure({
        placeholder: 'Write something for everyone and yourself...',
      }),
      Image.configure({
        inline: false,
        allowBase64: false,
      }),
      FileHandler.configure({
        allowedMimeTypes: ['image/png', 'image/jpeg', 'image/webp'],
        async onPaste(editor, files) {
          await handleImageUpload(editor, files)
        },

        async onDrop(editor, files) {
          await handleImageUpload(editor, files)
        },
      }),
      Youtube.configure({
        width: 480,
        height: 320,
        controls: false,
        nocookie: true,
      }),
  ],
})

onMounted(async () => {
  const response = await getTheSourceArticle(route.params.id)

  id.value = response.data.data.id
  title.value = response.data.data.title
  content.value = response.data.data.content

  title_editor.value.commands.setContent(title.value)
  content_editor.value.commands.setContent(content.value)
  emit('hydration-done')
})

const loading = ref(false);
const isSaving = ref(false);
const emit = defineEmits(['update', 'hydration-done', 'saved'])

async function handleSave() {
  isSaving.value = true;

  const titleText = title_editor.value.getText().trim();
  const contentJSON = content_editor.value.getJSON();

  try {
    await updateSourceArticle(id.value, titleText, contentJSON)
    toast.success("Article Saved!");
    emit('saved')

  } catch (error) {
    toast.error(error.response?.data?.message);
    console.error("Failed to save the article", error);

  } finally {
    isSaving.value = false;
  }
}

async function handleSubmit() {
  if (props.isDirty) {
    toast.error("Please save your changes before you submit!")
    return;
  }

  const id = route.params.id;

  loading.value = true;
  try {
    await submitArticle(id);
    toast.success("Article submitted successfully!");
    await router.push({ name: 'article-review', params: { id } });

  } catch (error) {
    toast.error(error.response?.data?.message);
    console.error("Failed to submit the article", error);

  } finally {
    loading.value = false;
  }
}

async function handleDelete() {
  loading.value = true;

  try {
    await deleteArticle(id.value);
    toast.success("Article deleted successfully!");
    await router.push({ name: 'my-articles' });

  } catch (error) {
    toast.error(error.response?.data?.message);
    console.error("Failed to delete the article", error);

  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <Teleport to="#page-header">
    <EditorToolBar
        v-if="content_editor"
        :editor="content_editor"
        :loading="loading"
        :is-saving="isSaving"
        :is-dirty="isDirty"
        @save="handleSave"
        @submit="handleSubmit"
        @delete="handleDelete"
    />
  </Teleport>


  <div class="flex flex-col px-3 py-5 mb-3 gap-y-5 w-3/5 shadow-md/25 border-t border-gray-100 flex-1 rounded-sm">

    <div class="editor-title rounded-lg p-3 bg-gray-200/60 text-light w-full">
      <EditorContent v-if="title_editor" :editor="title_editor"/>
    </div>

    <hr>

    <div class="editor-content p-3 text-light">
      <EditorContent v-if="content_editor" :editor="content_editor"/>
    </div>

  </div>

</template>
