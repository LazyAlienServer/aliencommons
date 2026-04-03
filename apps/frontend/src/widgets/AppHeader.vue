<script setup>
import {ref, computed, onMounted, onBeforeUnmount} from "vue";
import { RouterLink, useRouter } from "vue-router";
import { useUserStore, useThemeStore } from "@/features/user/stores";
import {
  YouTubeBlackIcon,
  GithubIcon,
  SunIcon,
  GearIcon,
  PersonIcon,
  PersonIconFillLarge,
  RepoIcon,
  RocketIcon,
  SignInIcon,
  SignOutIcon,
  XIcon,
  PlusIcon,
  TriangleDownIcon,
} from "@/core/assets/icons";
import { WebsiteIcon, LasLogo } from "@/core/assets";
import { createSourceArticle } from '@/features/articles/api';
import { useToast } from "vue-toastification";
import { useRoute } from "vue-router";

const route = useRoute();
const toast = useToast();
const router = useRouter();
const userStore = useUserStore();
const themeStore = useThemeStore();
const userInfo = computed(() => userStore.userInfo);
const avatarUrl = computed(() => import.meta.env.VITE_API_BASE_URL + userStore.userInfo.avatar)

const showPageHeader = computed(() => {
  const last = route.matched[route.matched.length - 1]
  return last?.meta?.showPageHeader === true
})

const isSidebarOpen = ref(false);
function toggleSidebar() {
  isSidebarOpen.value = !isSidebarOpen.value;
}

function toggleTheme() {
  themeStore.toggleTheme();
}

const loading = ref(false)

async function createArticle() {
  loading.value = true
  try {
    const response = await createSourceArticle()
    const id = response.data.data.id
    console.log("Article successfully created!")
    toggleCreate()
    await router.push({
      name: "article-editor",
      params: { id }
    })
  } catch (error) {
    toast.error(error.response?.data?.message);
    console.error("Failed to create a new article", error)
  } finally {
    loading.value = false
  }
}

// Create Dropdown

const isCreateOpen = ref(false);
const createRootElement = ref(null);

function toggleCreate() {
  isCreateOpen.value = !isCreateOpen.value;
}

const dropdowns = [
  { open: isCreateOpen, element: createRootElement },
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
</script>

<template>
  <header
      class="app-header header-backgrounds-auto"
      :class="showPageHeader ? 'border-0' : 'border-b border-neutral-300'"
  >
    <div class="flex flex-row items-center gap-6">

      <router-link :to="{ name: 'home' }">
        <WebsiteIcon class="w-8 h-auto"/>
      </router-link>

      <a href="https://lazyalienserver.top/" target="_blank" rel="noopener" class="w-9 h-auto">
        <LasLogo />
      </a>

      <router-link :to="{ name: 'published-article-list' }" class="ml-5">
        <span class="hover:text-blue-400 font-semibold">Articles</span>
      </router-link>

    </div>

    <div class="flex flex-row font-medium items-center gap-2">

      <div ref="createRootElement" class="relative">
        <button
            type="button"
            @click="toggleCreate()"
            class="header-icon flex flex-row items-center relative group"
        >

          <PlusIcon class="w-5 h-5 fill-current" />
          <TriangleDownIcon class="w-4 h-4 fill-current" />
          <span class="header-icon-tooltip">Create new...</span>

        </button>

        <div
            v-if="isCreateOpen"
            class="header-icon-dropdown"
        >

          <button
              type="button"
              class="header-icon-dropdown-btn"
              @click="createArticle()"
          >
            <RepoIcon class="sidebar-icon" />
            <span class="text-[15px]">New article</span>
          </button>

        </div>
      </div>

      <a href="https://www.youtube.com/@redstonevideotranslation5478" target="_blank" rel="noopener" class="header-icon group">
        <YouTubeBlackIcon class="w-5 h-5 fill-current" />
        <span class="header-icon-tooltip">Visit our YouTube</span>
      </a>

      <a href="https://github.com/LazyAlienServer" target="_blank" rel="noopener" class="header-icon group">
        <GithubIcon class="w-5 h-5 fill-current" />
        <span class="header-icon-tooltip">Visit our GitHub</span>
      </a>

      <div @click="toggleTheme" class="header-icon group">
        <SunIcon class="w-5 h-5 fill-current" />
        <span class="header-icon-tooltip">Toggle theme</span>
      </div>

      <img
          v-if="userInfo"
          :src="avatarUrl"
          alt="User Avatar"
          class="w-9 h-9 rounded-full object-cover ml-2 border border-gray-300"
          @click="toggleSidebar"
      />

      <div v-else class="header-icon">
        <PersonIconFillLarge class="w-6 h-6 fill-current" @click="toggleSidebar" />
      </div>

    </div>

    <!-- Mask -->
    <div
        v-if="isSidebarOpen"
        class="fixed inset-0 z-40 bg-gray-200 opacity-50"
        @click="toggleSidebar"
    >
    </div>

    <!-- Side Bar -->
    <div
        class="fixed top-0 right-0 z-50 h-full w-80 rounded-l-3xl shadow-lg transform transition-transform duration-300 backgrounds-auto"
        :class="isSidebarOpen ? 'translate-x-0' : 'translate-x-full'"
    >

      <!-- If user has signed in -->
      <div v-if="userInfo">
        <div class="absolute top-0 right-0 mt-8 mr-9 p-1 rounded-md hover:cursor-pointer hover:bg-gray-200 dark:hover:bg-[#2C2C2C]" @click="toggleSidebar">
          <XIcon class="sidebar-icon"/>
        </div>

        <div class="flex flex-col gap-4 p-6">
          <div class="flex flex-row items-center gap-3">
            <img
                :src="avatarUrl"
                alt="User Avatar"
                class="w-10 h-10 rounded-full object-cover border border-gray-300"
            />
            <p class="text-[17px] font-bold">{{ userInfo?.username }}</p>
          </div>

          <hr>

          <ul class="gap-y-3">
            <li>

              <router-link :to="{ name: 'profile', params: { username: userInfo?.username } }" class="sidebar-link" @click="toggleSidebar">
                <PersonIcon class="sidebar-icon" />
                Profile
              </router-link>
              <router-link :to="{ name: 'my-articles' }" class="sidebar-link" @click="toggleSidebar">
                <RepoIcon class="sidebar-icon" />
                Articles
              </router-link>
              <router-link :to="{ name: 'appearance' }" class="sidebar-link" @click="toggleSidebar">
                <GearIcon class="sidebar-icon" />
                Settings
              </router-link>

            </li>

            <hr class="my-3">

            <li>
              <router-link to="/logout" class="sidebar-link" @click="toggleSidebar">
                <SignOutIcon class="sidebar-icon" />
                Sign Out
              </router-link>
            </li>
          </ul>
        </div>
      </div>

      <!-- If user has not signed in -->
      <div v-else>
        <div class="flex flex-col gap-5 p-6">
          <div class="flex flex-row items-center gap-2">
            <PersonIconFillLarge class="w-8 h-8 fill-current" />
            <p class="text-[15px] font-bold">Anonymous User</p>
          </div>

          <hr>

          <ul class="space-y-3">
            <li>
              <router-link :to="{ name: 'login' }" class="sidebar-link" @click="toggleSidebar">
                <SignInIcon class="sidebar-icon" />
                Sign In
              </router-link>
              <router-link :to="{ name: 'register' }" class="sidebar-link" @click="toggleSidebar">
                <RocketIcon class="sidebar-icon" />
                Sign up
              </router-link>
            </li>
          </ul>
        </div>
      </div>

    </div>

  </header>
</template>

