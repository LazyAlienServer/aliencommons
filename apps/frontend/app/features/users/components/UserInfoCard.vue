<script setup lang="ts">
import { ref, computed } from "vue";
import { updateAvatar, updateUsername } from "@/features/users/api/user";
import { useToast } from "vue-toastification";
import { PencilIcon, PersonIcon, MailIcon, RocketIcon } from "~/assets/icons";

const toast = useToast();
const userStore = useUserStore();
const userInfo = computed(() => userStore.userInfo);
const avatarUrl = computed(
  () => import.meta.env.VITE_API_BASE_URL + userStore.userInfo.avatar,
);

const fileInput = ref<HTMLInputElement | undefined>(undefined);

// Open File Select Window
function triggerFileSelect() {
  fileInput.value.click();
}

// Handle File Upload
async function handleFile(event) {
  const file = event.target.files[0];
  if (!file) return;

  try {
    const response = await updateAvatar(file);
    userInfo.value = response.data.data;
    toast.success("Avatar updated successfully!");
  } catch (error) {
    toast.error(error.response?.data?.message);
    console.error("Avatar update failed:", error);
  }
}

// Edit Username
const isInputOpen = ref(false);
const newUsername = ref("");
const loading = ref(false);

function toggleInput() {
  isInputOpen.value = !isInputOpen.value;
}

async function handleUsernameUpdate() {
  loading.value = true;

  try {
    const response = await updateUsername(newUsername.value);
    userInfo.value = response.data.data;
    toast.success("Username updated successfully!");
  } catch (error) {
    const msg = error.response?.data?.message;
    toast.error(msg);
    console.error("Update username failed", error);
  } finally {
    toggleInput();
    loading.value = false;
  }
}
</script>

<template>
  <div v-if="userInfo" class="mt-3 mr-15 flex h-full w-1/5 flex-col gap-5">
    <div class="relative flex flex-col items-center gap-y-7">
      <img
        :src="avatarUrl"
        alt="User Avatar"
        class="h-55 w-55 rounded-full border border-gray-300 object-cover"
      />

      <PencilIcon
        @click="triggerFileSelect"
        class="absolute top-0 right-0 h-6 w-6 -translate-x-4 translate-y-4 transform rounded-full fill-current p-1 shadow-lg"
      />

      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        class="hidden"
        @change="handleFile"
      />
    </div>

    <!-- Edit username -->
    <div v-if="isInputOpen" class="flex flex-col items-center gap-3">
      <input
        v-model="newUsername"
        type="text"
        placeholder="        New Username"
        class="username-input"
      />

      <div class="flex flex-row items-center gap-3">
        <button
          @click="handleUsernameUpdate"
          :disabled="loading"
          class="form-btn"
        >
          Save
        </button>
        <button
          @click="toggleInput"
          :disabled="loading"
          class="form-btn bg-gray-400 hover:bg-gray-500"
        >
          Cancel
        </button>
      </div>
    </div>

    <div v-else class="flex flex-col items-center gap-4">
      <!-- username & edit toggle button-->
      <p class="text-2xl font-bold">{{ userInfo.username }}</p>

      <div
        class="flex flex-row items-center gap-x-2 rounded-lg border border-gray-400 px-4 py-1 hover:bg-gray-300"
        @click="toggleInput"
      >
        <PencilIcon class="h-4.5 w-4.5 fill-current" />
        <p class="text-[16px]">Edit Your Username</p>
      </div>

      <!-- Other user info -->
      <div class="mt-2 flex flex-col gap-2 pl-2">
        <div class="flex flex-row items-center gap-1">
          <PersonIcon class="h-4.5 w-4.5 fill-current" />
          <p class="text-[16px]">ID: {{ userInfo.id }}</p>
        </div>

        <div class="flex flex-row items-center gap-1">
          <MailIcon class="h-4.5 w-4.5 fill-current" />
          <p class="text-[16px]">Email: {{ userInfo.email }}</p>
        </div>

        <div class="flex flex-row items-center gap-1">
          <RocketIcon class="h-4.5 w-4.5 fill-current" />
          <p class="text-[16px]">
            Joined Since:
            {{ new Date(userInfo.date_joined).toLocaleDateString() }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
