<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import {
  ArrowLeftToLine,
  Undo2,
  Redo2,
  ChevronDown,
  Heading,
  Heading1,
  Heading2,
  Heading3,
  List,
  ListOrdered,
  ListTodo,
  TextQuote,
  SquareCode,
  MessageSquareDiff,
  Bold,
  Italic,
  Strikethrough,
  CodeXml,
  Underline,
  Highlighter,
  Link,
  Omega,
  Superscript,
  Subscript,
  TextAlignStart,
  TextAlignEnd,
  TextAlignCenter,
  TextAlignJustify,
  Image,
  Youtube,
  Save,
  BookUp,
  Ellipsis,
  FlameKindling,
} from 'lucide-vue-next'
import { RouterLink } from "vue-router";
import { BaseModal } from '@/core/components';
import { uploadArticleImage } from "@/features/articles/api";
import { useToast } from "vue-toastification";

const toast = useToast();
const open = ref(false);

const props = defineProps({
  editor: {
    type: Object,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
    required: true
  },
  isSaving: {
    type: Boolean,
    default: false,
    required: true
  },
  isDirty: {
    type: Boolean,
    required: true,
  }
})

const isHeading1 = computed(() => props.editor.isActive('heading', { level: 1 }))
const isHeading2 = computed(() => props.editor.isActive('heading', { level: 2 }))
const isHeading3 = computed(() => props.editor.isActive('heading', { level: 3 }))
const isBulletList = computed(() => props.editor.isActive('bulletList'))
const isOrderedList = computed(() => props.editor.isActive('orderedList'))
const isTaskList = computed(() => props.editor.isActive('taskList'))
const isBlockquote = computed(() => props.editor.isActive('blockquote'))
const isCodeBlock = computed(() => props.editor.isActive('codeBlock'))
const isBold = computed(() => props.editor.isActive('bold'))
const isItalic = computed(() => props.editor.isActive('italic'))
const isStrike = computed(() => props.editor.isActive('strike'))
const isCode = computed(() => props.editor.isActive('code'))
const isUnderline = computed(() => props.editor.isActive('underline'))
const isHighlight = computed(() => props.editor.isActive('highlight'))
const isLink = computed(() => props.editor.isActive('link'))
const isSuperscript = computed(() => props.editor.isActive('superscript'))
const isSubscript = computed(() => props.editor.isActive('subscript'))
const isAlignLeft = computed(() => props.editor.isActive({ textAlign: 'left' }))
const isAlignRight = computed(() => props.editor.isActive({ textAlign: 'right' }))
const isAlignCenter = computed(() => props.editor.isActive({ textAlign: 'center' }))
const isAlignJustify = computed(() => props.editor.isActive({ textAlign: 'justify' }))

// Link Extension
function setLink() {
  const previousUrl = props.editor.getAttributes('link').href
  const url = window.prompt('Please enter the URL:', previousUrl)

  if (url === null) {
    return
  }

  if (url === '') {
    props.editor.chain().focus().extendMarkRange('link').unsetLink().run()
    return
  }

  props.editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
}

// Mathematics Extension
function insertInlineMath() {
  const hasSelection = !props.editor.state.selection.empty
  if (hasSelection) {
    return props.editor.chain().setInlineMath().focus().run()
  }

  const latex = prompt('Enter inline math expression:', '')
  return props.editor.chain().insertInlineMath({ latex }).focus().run()
}

function insertBlockMath() {
  const hasSelection = !props.editor.state.selection.empty
  if (hasSelection) {
    return props.editor.chain().setBlockMath().focus().run()
  }

  const latex = prompt('Enter block math expression:', '')
  return props.editor.chain().insertBlockMath({ latex }).focus().run()
}

// Dropdown Menus
const isHeadingOpen = ref(false)
const isListOpen = ref(false)
const isAlignOpen = ref(false)
const isActionOpen = ref(false)

const headingRootElement = ref(null)
const listRootElement = ref(null)
const alignRootElement = ref(null)
const actionRootElement = ref(null)

function toggleHeading() {
  isHeadingOpen.value = !isHeadingOpen.value
}
function toggleList() {
  isListOpen.value = !isListOpen.value
}
function toggleAlign() {
  isAlignOpen.value = !isAlignOpen.value
}
function toggleAction() {
  isActionOpen.value = !isActionOpen.value
}

const dropdowns = [
  { open: isHeadingOpen, element: headingRootElement },
  { open: isListOpen, element: listRootElement },
  { open: isAlignOpen, element: alignRootElement },
  { open: isActionOpen, element: actionRootElement },
]

function closeAll() {
  dropdowns.forEach((d) => (d.open.value = false))
}

function onWindowClick(event) {
  const target = event.target

  dropdowns.forEach(({ open, element }) => {
    if (!open.value) return

    const rootElement = element.value
    // What if .contains() throws an error???
    if (!rootElement) {
      open.value = false
      return
    }

    if (!rootElement.contains(target)) {
      open.value = false
    }
  })
}

function onKeyDown(event) {
  if (event.key === 'Escape') closeAll()
}

onMounted(() => {
  window.addEventListener('click', onWindowClick, true)
  window.addEventListener('keydown', onKeyDown)
})
onBeforeUnmount(() => {
  window.removeEventListener('click', onWindowClick, true)
  window.removeEventListener('keydown', onKeyDown)
})

// Add Image Button
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
      console.error('Image upload failed', error)
      toast.error('Image upload failed')
    }
  }
}

const fileInputRef = ref(null)

async function onPickFile(event) {
  const file = event.target.files?.[0]
  if (!file) return

  event.target.value = ''

  await handleImageUpload(props.editor, [file])
}

function openFilePicker() {
  fileInputRef.value?.click()
}

// YouTube Button
function addVideo() {
  const url = prompt('Enter YouTube URL')

  props.editor.commands.setYoutubeVideo({
    src: url,
  })
}
</script>

<template>
  <div class="flex flex-row justify-between flex-1">

    <!-- Left Section -->
    <div class="flex flex-row justify-center items-center w-1/7">

      <div class="flex-1/2 flex flex-row items-center justify-center">
        <router-link
            :to="{ name: 'my-articles' }"
            class="editor-actions-btn group"
        >
          <ArrowLeftToLine size="21"/>
          <span class="editor-toolbar-btn-tooltip">Back to my articles</span>
        </router-link>
      </div>

      <div class="flex-1/2 flex flex-row items-center justify-center">
        <span class="text-[10px] font-semibold" v-if="isSaving">
          Saving
        </span>
        <span class="text-[10px] font-semibold" v-else-if="isDirty">
          Changes not saved
        </span>
        <span class="text-[10px] font-semibold" v-else>
          Changes saved
        </span>
      </div>

    </div>

    <!-- Center Section -->
    <div class="flex flex-row justify-center gap-2 p-2 items-center w-5/7">

      <button
          type="button"
          class="editor-toolbar-btn group"
          :disabled="!editor?.can().chain().focus().undo().run()"
          @click="editor.chain().focus().undo().run()"
      >
        <Undo2 size="17"/>
        <span class="editor-toolbar-btn-tooltip">Undo</span>
      </button>

      <button
          type="button"
          class="editor-toolbar-btn group"
          :disabled="!editor?.can().chain().focus().redo().run()"
          @click="editor.chain().focus().redo().run()"
      >
        <Redo2 size="17"/>
        <span class="editor-toolbar-btn-tooltip">Redo</span>
      </button>

      <div class="w-[0.1px] mx-1 bg-black h-full"></div>

      <div ref="headingRootElement" class="relative">
        <button
            type="button"
            class="editor-toolbar-btn group"
            :class="{ active: isHeading1 || isHeading2 || isHeading3 }"
            @click="toggleHeading()"
        >
          <Heading size="17" :class="{ active: isHeading1 || isHeading2 || isHeading3 }" class="editor-toolbar-svg"/>
          <ChevronDown size="10"/>
          <span class="editor-toolbar-btn-tooltip">Headings</span>
        </button>

        <!-- Heading Dropdown Menu -->
        <div
            v-if="isHeadingOpen"
            class="editor-toolbar-dropdown"
        >

          <button
              type="button"
              class="editor-toolbar-dropdown-btn"
              :class="{ active: isHeading1 }"
              @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
          >
            <Heading1 size="17" :class="{ active: isHeading1 }" class="editor-toolbar-svg"/>
            <span class="text-[15px]">Heading 1</span>
          </button>

          <button
              type="button"
              class="editor-toolbar-dropdown-btn"
              :class="{ active: isHeading2 }"
              @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
          >
            <Heading2 size="17" :class="{ active: isHeading2 }" class="editor-toolbar-svg"/>
            <span class="text-[15px]">Heading 2</span>
          </button>

          <button
              type="button"
              class="editor-toolbar-dropdown-btn"
              :class="{ active: isHeading3 }"
              @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
          >
            <Heading3 size="17" :class="{ active: isHeading3 }" class="editor-toolbar-svg"/>
            <span class="text-[15px]">Heading 3</span>
          </button>

        </div>
      </div>

      <div ref="listRootElement" class="relative">
        <button
            type="button"
            class="editor-toolbar-btn group"
            :class="{ active: isBulletList || isOrderedList || isTaskList }"
            @click="toggleList()"
        >
          <List size="17" :class="{ active: isBulletList || isOrderedList || isTaskList }" class="editor-toolbar-svg"/>
          <ChevronDown size="10"/>
          <span class="editor-toolbar-btn-tooltip">Lists</span>
        </button>

        <!-- List Dropdown Menu -->
        <div
            v-if="isListOpen"
            class="editor-toolbar-dropdown"
        >

          <button
              type="button"
              class="editor-toolbar-dropdown-btn"
              :class="{ active: isBulletList }"
              @click="editor.chain().focus().toggleBulletList().run()"
          >
            <List size="17" :class="{ active: isBulletList }" class="editor-toolbar-svg"/>
            <span class="text-[15px]">Bullet List</span>
          </button>

          <button
              type="button"
              class="editor-toolbar-dropdown-btn"
              :class="{ active: isOrderedList }"
              @click="editor.chain().focus().toggleOrderedList().run()"
          >
            <ListOrdered size="17" :class="{ active: isOrderedList }" class="editor-toolbar-svg"/>
            <span class="text-[15px]">Ordered List</span>
          </button>

          <button
              type="button"
              class="editor-toolbar-dropdown-btn"
              :class="{ active: isTaskList }"
              @click="editor.chain().focus().toggleTaskList().run()"
          >
            <ListTodo size="17" :class="{ active: isTaskList }" class="editor-toolbar-svg"/>
            <span class="text-[15px]">Task List</span>
          </button>

        </div>
      </div>

      <div ref="alignRootElement" class="relative">
        <button
            type="button"
            class="editor-toolbar-btn group"
            :class="{ active: isAlignLeft || isAlignRight || isAlignCenter || isAlignJustify }"
            @click="toggleAlign()"
        >
          <TextAlignStart size="17" :class="{ active: isAlignLeft || isAlignRight || isAlignCenter || isAlignJustify }" class="editor-toolbar-svg"/>
          <ChevronDown size="10"/>
          <span class="editor-toolbar-btn-tooltip">Text aligns</span>
        </button>

        <!-- List Dropdown Menu -->
        <div
            v-if="isAlignOpen"
            class="editor-toolbar-dropdown"
        >

          <button
              type="button"
              class="editor-toolbar-dropdown-btn"
              :class="{ active: isAlignLeft }"
              @click="editor.chain().focus().toggleTextAlign('left').run()"
          >
            <TextAlignStart size="17" :class="{ active: isAlignLeft }" class="editor-toolbar-svg"/>
            <span class="text-[15px]">Align Left</span>
          </button>

          <button
              type="button"
              class="editor-toolbar-dropdown-btn"
              :class="{ active: isAlignRight }"
              @click="editor.chain().focus().toggleTextAlign('right').run()"
          >
            <TextAlignEnd size="17" :class="{ active: isAlignRight }" class="editor-toolbar-svg"/>
            <span class="text-[15px]">Align Right</span>
          </button>

          <button
              type="button"
              class="editor-toolbar-dropdown-btn"
              :class="{ active: isAlignCenter }"
              @click="editor.chain().focus().toggleTextAlign('center').run()"
          >
            <TextAlignCenter size="17" :class="{ active: isAlignCenter }" class="editor-toolbar-svg"/>
            <span class="text-[15px]">Align Center</span>
          </button>

          <button
              type="button"
              class="editor-toolbar-dropdown-btn"
              :class="{ active: isAlignJustify }"
              @click="editor.chain().focus().toggleTextAlign('justify').run()"
          >
            <TextAlignJustify size="17" :class="{ active: isAlignJustify }" class="editor-toolbar-svg"/>
            <span class="text-[15px]">Align Justify</span>
          </button>

        </div>
      </div>

      <div class="w-[0.1px] mx-1 bg-black h-full"></div>

      <button
          type="button"
          class="editor-toolbar-btn group"
          :class="{ active: isBlockquote }"
          @click="editor.chain().focus().toggleBlockquote().run()"
      >
        <TextQuote size="17" :class="{ active: isBlockquote }" class="editor-toolbar-svg"/>
        <span class="editor-toolbar-btn-tooltip">Block quote</span>
      </button>

      <button
          type="button"
          class="editor-toolbar-btn group"
          :class="{ active: isCodeBlock }"
          @click="editor.chain().focus().toggleCodeBlock().run()"
      >
        <SquareCode size="17" :class="{ active: isCodeBlock }" class="editor-toolbar-svg"/>
        <span class="editor-toolbar-btn-tooltip">Block code</span>
      </button>

      <button
          type="button"
          class="editor-toolbar-btn group"
          @click="insertBlockMath()"
      >
        <MessageSquareDiff size="17" class="editor-toolbar-svg"/>
        <span class="editor-toolbar-btn-tooltip">Block math</span>
      </button>

      <div class="w-[0.1px] mx-1 bg-black h-full"></div>

      <button
          type="button"
          class="editor-toolbar-btn group"
          :class="{ active: isBold }"
          @click="editor.chain().focus().toggleBold().run()"
      >
        <Bold size="17" :class="{ active: isBold }" class="editor-toolbar-svg"/>
        <span class="editor-toolbar-btn-tooltip">Bold</span>
      </button>

      <button
          type="button"
          class="editor-toolbar-btn group"
          :class="{ active: isItalic }"
          @click="editor.chain().focus().toggleItalic().run()"
      >
        <Italic size="17" :class="{ active: isItalic }" class="editor-toolbar-svg"/>
        <span class="editor-toolbar-btn-tooltip">Italic</span>
      </button>

      <button
          type="button"
          class="editor-toolbar-btn group"
          :class="{ active: isStrike }"
          @click="editor.chain().focus().toggleStrike().run()"
      >
        <Strikethrough size="17" :class="{ active: isStrike }" class="editor-toolbar-svg"/>
        <span class="editor-toolbar-btn-tooltip">Strike</span>
      </button>

      <button
          type="button"
          class="editor-toolbar-btn group"
          :class="{ active: isCode }"
          @click="editor.chain().focus().toggleCode().run()"
      >
        <CodeXml size="17" :class="{ active: isCode }" class="editor-toolbar-svg"/>
        <span class="editor-toolbar-btn-tooltip">Code</span>
      </button>

      <button
          type="button"
          class="editor-toolbar-btn group"
          :class="{ active: isUnderline }"
          @click="editor.chain().focus().toggleUnderline().run()"
      >
        <Underline size="17" :class="{ active: isUnderline }" class="editor-toolbar-svg"/>
        <span class="editor-toolbar-btn-tooltip">Underline</span>
      </button>

      <button
          type="button"
          class="editor-toolbar-btn group"
          :class="{ active: isHighlight }"
          @click="editor.chain().focus().toggleHighlight().run()"
      >
        <Highlighter size="17" :class="{ active: isHighlight }" class="editor-toolbar-svg"/>
        <span class="editor-toolbar-btn-tooltip">Highlight</span>
      </button>

      <button
          type="button"
          class="editor-toolbar-btn group"
          :class="{ active: isLink }"
          @click="setLink()"
      >
        <Link size="17" :class="{ active: isLink }" class="editor-toolbar-svg"/>
        <span class="editor-toolbar-btn-tooltip">Link</span>
      </button>

      <div class="w-[0.1px] mx-1 bg-black h-full"></div>

      <button
          type="button"
          class="editor-toolbar-btn group"
          @click="insertInlineMath()"
      >
        <Omega size="17" class="editor-toolbar-svg"/>
        <span class="editor-toolbar-btn-tooltip">Math</span>
      </button>

      <button
          type="button"
          class="editor-toolbar-btn group"
          :class="{ active: isSuperscript }"
          @click="editor.chain().focus().toggleSuperscript().run()"
      >
        <Superscript size="17" :class="{ active: isSuperscript }" class="editor-toolbar-svg"/>
        <span class="editor-toolbar-btn-tooltip">Superscript</span>
      </button>

      <button
          type="button"
          class="editor-toolbar-btn group"
          :class="{ active: isSubscript }"
          @click="editor.chain().focus().toggleSubscript().run()"
      >
        <Subscript size="17" :class="{ active: isSubscript }" class="editor-toolbar-svg"/>
        <span class="editor-toolbar-btn-tooltip">Subscript</span>
      </button>

      <div class="w-[0.1px] mx-1 bg-black h-full"></div>

      <div class="flex flex-row items-center">
        <button
            type="button"
            class="editor-toolbar-btn group"
            @click="openFilePicker()"
        >
          <Image size="17"/>
          <span class="editor-toolbar-btn-tooltip">Add image</span>
        </button>

        <input
            ref="fileInputRef"
            type="file"
            accept=".jpg, .jpeg, .png, .webp"
            class="hidden"
            @change="onPickFile"
        />
      </div>

      <button
          type="button"
          class="editor-toolbar-btn group"
          @click="addVideo()"
      >
        <Youtube size="17"/>
        <span class="editor-toolbar-btn-tooltip">Embed YouTube video</span>
      </button>

    </div>

    <!-- Right Section -->
    <div class="flex flex-row justify-center gap-2 items-center w-1/7">
      <button
          type="button"
          class="editor-actions-btn group"
          :disabled="isSaving"
          @click="$emit('save')"
      >
        <Save size="21"/>
        <span class="editor-toolbar-btn-tooltip">Save changes</span>
      </button>

      <button
          type="button"
          class="editor-actions-btn group"
          :disabled="loading"
          @click="$emit('submit')"
      >
        <BookUp size="21"/>
        <span class="editor-toolbar-btn-tooltip">Submit for review</span>
      </button>

      <div ref="actionRootElement" class="relative">
        <button
            type="button"
            class="editor-actions-btn group"
            @click="toggleAction()"
        >
          <Ellipsis size="21"/>
          <ChevronDown size="10"/>
          <span class="editor-toolbar-btn-tooltip">More actions...</span>
        </button>

        <!-- Action Dropdown Menu -->
        <div
            v-if="isActionOpen"
            class="editor-actions-dropdown"
        >

          <button
              type="button"
              class="editor-actions-dropdown-btn bg-red-200 hover:bg-red-300"
              @click="open = true"
          >
            <FlameKindling size="17"/>
            <span class="text-[15px]">Delete</span>
          </button>

          <BaseModal v-model="open">
            <div class="flex flex-col p-6 w-115 gap-y-6">

              <div class="flex flex-col gap-y-4">
                <h2 class="text-lg font-semibold">Are you sure?</h2>
                <p class="text-sm text-gray-600">
                  This operation cannot be undone.
                </p>
              </div>

              <div class="flex flex-row justify-end gap-x-5">
                <button
                    class="bg-gray-200 px-4 py-2 rounded hover:bg-gray-300"
                    @click="open = false"
                >
                  Cancel
                </button>
                <button
                    class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-700"
                    @click="$emit('delete')"
                >
                  Delete
                </button>
              </div>

            </div>
          </BaseModal>

        </div>
      </div>
    </div>
  </div>
</template>
