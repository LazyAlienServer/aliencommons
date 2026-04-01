<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { createProfile } from '@/features/user/api'
import { useToast } from "vue-toastification";
import { MailIcon, KeyIcon } from "@/assets/icons"

const router = useRouter();
const toast = useToast();

const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const loading = ref(false);

async function handleRegister() {
  loading.value = true;

  try {
    await createProfile(email.value, password.value, confirmPassword.value);
    toast.success('Successfully signed up!');
    await router.push({ name: 'login' });

  } catch (error) {
    const msg = error.response?.data?.message
    toast.error(msg)
    console.error("Register failed, ", error)

  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <form @submit.prevent="handleRegister" class="backgrounds-auto gap-4">
    <h2 class="text-2xl font-bold text-center">Sign Up</h2>

    <div>
      <div class="flex flex-row items-center gap-2">
        <MailIcon class="login-register-icon" />
        <label for="email" class="block mb-1 font-medium">Email</label>
      </div>
      <input
          v-model="email"
          id="email"
          type="email"
          required
          autocomplete="off"
          class="login-register-input"
      />
    </div>

    <div>
      <div class="flex flex-row items-center gap-2">
        <KeyIcon class="login-register-icon" />
        <label for="password" class="block mb-1 font-medium">Password</label>
      </div>
      <input
          v-model="password"
          id="password"
          type="password"
          required
          autocomplete="new-password"
          class="login-register-input"
      />
    </div>

    <div>
      <div class="flex flex-row items-center gap-2">
        <KeyIcon class="login-register-icon" />
        <label for="confirmPassword" class="block mb-1 font-medium">Confirm Password</label>
      </div>
      <input
          v-model="confirmPassword"
          id="confirmPassword"
          type="password"
          required
          autocomplete="new-password"
          class="login-register-input"
      />
    </div>

    <div class="flex flex-col items-start gap-1">
      <p class="text-[12px]">Your password:</p>
      <p class="text-[12px]">- can't be less than 8 characters.</p>
      <p class="text-[12px]">- can’t be entirely numeric.</p>
      <p class="text-[12px]">- can’t be a commonly used password.</p>
      <p class="text-[12px]">- can’t be too similar to your other personal information.</p>
    </div>

    <button type="submit" :disabled="loading" class="form-btn">
      Sign up
    </button>

    <router-link :to="{ name: 'login' }" class="link">
      Already had an account? Sign in here
    </router-link>

  </form>

</template>

<style scoped>

</style>