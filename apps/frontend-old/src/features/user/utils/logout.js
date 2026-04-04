import { useUserStore } from "@/features/user/stores";


function handleLogout() {
    const userStore = useUserStore();
    userStore.logout();
}

export {
    handleLogout,
}
