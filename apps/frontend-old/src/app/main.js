import { createApp } from 'vue';
import { createPinia } from "pinia";
import App from './App.vue';
import router from "src/app/router";
import "@/core/styles/css/app.css";
import "@/core/styles/css/article.css";
import "@/core/styles/css/modal.css";
import "@/core/styles/css/katex.css"
import { setupGlobalErrorHandler } from "@/core/utils";
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";
import { useThemeStore, useUserStore } from "@/features/user/stores";


const app = createApp(App);

app.use(router);
app.use(createPinia());
app.use(Toast, {
    position: "top-center",
    timeout: 3500,
    closeOnClick: true,
})

setupGlobalErrorHandler(app);

const themeStore = useThemeStore();
themeStore.initTheme();
const userStore = useUserStore();
userStore.initUser()
    .catch(() => {userStore.logout();})

app.mount('#app');
