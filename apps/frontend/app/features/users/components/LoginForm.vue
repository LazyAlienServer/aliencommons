<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { MailIcon, KeyIcon } from "~/assets/icons";

const toast = useToast();
const router = useRouter();
const userStore = useUserStore();

const email = ref("");
const password = ref("");
const loading = ref(false);

async function handleLogin() {
  loading.value = true;

  try {
    await userStore.login(email.value, password.value);
    toast.success("Sign in successful!");
    await router.push({ name: "home" });
  } catch (error) {
    toast.error(error.response?.data?.message);
    console.error("Login failed", error);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <form @submit.prevent="handleLogin" class="backgrounds-auto gap-4">
    <h2 class="text-center text-2xl font-bold">Sign In</h2>

    <div>
      <div class="flex flex-row items-center gap-2">
        <MailIcon class="login-register-icon" />
        <label for="email" class="mb-1 block font-medium">Email</label>
      </div>
      <input
        v-model="email"
        id="email"
        type="email"
        required
        class="login-register-input"
      />
    </div>

    <div>
      <div class="flex flex-row items-center gap-2">
        <KeyIcon class="login-register-icon" />
        <label for="password" class="mb-1 block font-medium">Password</label>
      </div>
      <input
        v-model="password"
        id="password"
        type="password"
        required
        class="login-register-input"
      />
    </div>

    <button type="submit" :disabled="loading" class="form-btn">Sign in</button>

    <router-link :to="{ name: 'register' }" class="link">
      Do not have an account? Sign up here
    </router-link>
  </form>
</template>
