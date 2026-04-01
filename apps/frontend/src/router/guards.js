import { useUserStore } from "@/features/user/stores";


async function globalBeforeEach(to) {
    const userStore = useUserStore();

    const isLoggedIn = userStore.isLoggedIn;

    if (to.meta.requiresAuth && !isLoggedIn) {
        return { name: 'login' };
    }

    if ((to.name === "login" || to.name === "register") && isLoggedIn) {
        return { name: 'home' };
    }

    if (to.meta.title) {
        document.title = to.meta.title;
    }
}


export {
    globalBeforeEach,
}
