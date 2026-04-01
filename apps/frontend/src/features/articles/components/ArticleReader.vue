<script setup>
import { computed } from 'vue'
import { generateHTML } from '@tiptap/core'
import StarterKit from "@tiptap/starter-kit";
import { TaskItem, TaskList } from "@tiptap/extension-list";
import Superscript from "@tiptap/extension-superscript";
import Subscript from "@tiptap/extension-subscript";
import Highlight from "@tiptap/extension-highlight";
import TextAlign from "@tiptap/extension-text-align";
import { Mathematics } from "@tiptap/extension-mathematics";
import Image from "@tiptap/extension-image";
import Youtube from "@tiptap/extension-youtube";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  content: {
    type: Object,
    required: true,
  }
})

const extensions = [
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
  Mathematics,
  Image.configure({
    inline: false,
    allowBase64: false,
  }),
  Youtube.configure({
    width: 480,
    height: 320,
    controls: false,
    nocookie: true,
  }),
]
// Generate HTML from JSON
const html = computed(() => {
  try {
    return generateHTML(props.content, extensions)
  } catch (error) {
    console.error("Failed to render content", error)
    return "<p class='text-red-600'>Failed to render content.</p>"
  }
})
</script>

<template>

  <article class="flex flex-col flex-1 w-3/5 min-h-screen">
    <!-- title -->
    <h1 class="text-[40px] font-semibold mb-6">{{ title || "Untitled"}}</h1>

    <!-- content -->
    <div class="ProseMirror" v-html="html" />
  </article>
  
</template>
