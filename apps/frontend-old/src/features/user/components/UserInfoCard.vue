<script setup>
import { ref, computed } from "vue";
import { useUserStore } from "@/features/user/stores";
import { updateAvatar, updateUsername } from "@/features/user/api";
import { useToast } from "vue-toastification";
import { PencilIcon, PersonIcon, MailIcon, RocketIcon } from "@/core/assets/icons"

const toast = useToast();
const userStore = useUserStore();
const userInfo = computed(() => userStore.userInfo);
const avatarUrl = computed(() => import.meta.env.VITE_API_BASE_URL + userStore.userInfo.avatar)

const fileInput = ref(null);

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
    userInfo.value = response.data.data
    toast.success('Avatar updated successfully!');

  } catch (error) {
    toast.error(error.response?.data?.message);
    console.error('Avatar update failed:', error);
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
    const response = await updateUsername(newUsername.value)
    userInfo.value = response.data.data
    toast.success('Username updated successfully!');

  } catch (error) {
    const msg = error.response?.data?.message
    toast.error(msg);
    console.error('Update username failed', error)

  } finally {
    toggleInput()
    loading.value = false;
  }
}
</script>

<template>
  <div v-if="userInfo" class="flex flex-col gap-5 mr-15 mt-3 h-full w-1/5">
    <div class="flex flex-col gap-y-7 items-center relative">

      <img
          :src="avatarUrl"
          alt="User Avatar"
          class="w-55 h-55 rounded-full object-cover border border-gray-300"
      />

      <PencilIcon
          @click="triggerFileSelect"
          class="w-6 h-6 fill-current absolute top-0 right-0 rounded-full p-1 shadow-lg transform -translate-x-4 translate-y-4"
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
    <div
        v-if="isInputOpen"
        class="flex flex-col items-center gap-3"
    >

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
            class="bg-gray-400 hover:bg-gray-500 form-btn"
        >
          Cancel
        </button>

      </div>

    </div>

    <div v-else class="flex flex-col items-center gap-4">

      <!-- username & edit toggle button-->
      <p class="text-2xl font-bold">{{ userInfo.username }}</p>

      <div
          class="flex flex-row items-center gap-x-2 rounded-lg border border-gray-400 hover:bg-gray-300 px-4 py-1"
          @click="toggleInput"
      >

        <PencilIcon class="w-4.5 h-4.5 fill-current"/>
        <p class="text-[16px]">Edit Your Username</p>

      </div>

      <!-- Other user info -->
      <div class="flex flex-col pl-2 mt-2 gap-2">

        <div class="flex flex-row items-center gap-1">
          <PersonIcon class="w-4.5 h-4.5 fill-current"/>
          <p class="text-[16px]">ID: {{ userInfo.id }}</p>
        </div>

        <div class="flex flex-row items-center gap-1">
          <MailIcon class="w-4.5 h-4.5 fill-current"/>
          <p class="text-[16px]">Email: {{ userInfo.email }}</p>
        </div>

        <div class="flex flex-row items-center gap-1">
          <RocketIcon class="w-4.5 h-4.5 fill-current"/>
          <p class="text-[16px]">Joined Since: {{ new Date(userInfo.date_joined).toLocaleDateString() }}</p>
        </div>

      </div>

    </div>

  </div>
</template>