<script setup>
import { computed } from "vue";
import { useUserStore } from "@/features/user/stores";
import { handleLogout } from "@/features/user/utils";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification"

const userStore = useUserStore();
const toast = useToast();
const router = useRouter();
const userInfo = computed(() => userStore.userInfo);
const avatarUrl = computed(() => import.meta.env.VITE_API_BASE_URL + userStore.userInfo.avatar)

function onLogout() {
  handleLogout();
  toast.success("Sign out successful!");
  router.push({name: "home"});
}
</script>

<template>
  <div v-if="userInfo" class="flex flex-col gap-y-6 self-center items-center">

    <h2>Are you sure?</h2>

    <div>
      <img
          :src="avatarUrl"
          alt="User Avatar"
          class="w-24 h-24 rounded-full object-cover border border-gray-300"
      />
    </div>

    <p><b>Username: </b>{{ userInfo.username }}</p>
    <p><b>Email: </b>{{ userInfo.email }}</p>

    <button @click="onLogout" class="form-btn">
      Sign out
    </button>

  </div>
</template>
