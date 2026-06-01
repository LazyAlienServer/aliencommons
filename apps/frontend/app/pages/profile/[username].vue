<script setup lang="ts">
import { UserInfoCard, Profile } from "@/features/users/components";

definePageMeta({
  name: "profile",
});
</script>

<template>
  <div class="row-body-container">
    <UserInfoCard />
    <Profile />
  </div>
</template>
