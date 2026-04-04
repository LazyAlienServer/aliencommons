import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { retrieveMyProfile, loginUser, refreshUserLoginToken } from "@/features/user/api";
import { setRefreshToken, getRefreshToken, removeRefreshToken } from "@/core/utils";

export const useUserStore = defineStore('user', () => {
    /* states */
    const accessToken = ref(null);
    const userInfo = ref(null);
    const isLoggedIn = computed(() => !!accessToken.value);


    /* Tools */
    const refreshTimer = ref(null);

    function scheduleTokenRefresh(expiresInSeconds) {
        // 可能有问题
        clearTimeout(refreshTimer);
        const refreshDelay = (expiresInSeconds - 60) * 1000;

        refreshTimer.value = setTimeout(() => {
            refreshAccessToken()
                .then(() => {console.log("Access token successfully refreshed!")})
                .catch((error) => {console.warn(error);})
        }, refreshDelay);
    }

    /* actions */
    async function loadUserInfo() {
        const response = await retrieveMyProfile();

        userInfo.value = response.data.data;
    }

    async function login(email, password) {
        const response = await loginUser(email, password);

        accessToken.value = response.data.data.access;

        localStorage.setItem("accessToken", accessToken.value);
        setRefreshToken(response.data.data.refresh, parseInt(response.data.data.refresh_token_lifetime));

        await loadUserInfo();

        scheduleTokenRefresh(parseInt(response.data.data.access_token_lifetime));
    }

    async function refreshAccessToken() {
        const response = await refreshUserLoginToken(getRefreshToken());

        accessToken.value = response.data.data.access;
        localStorage.setItem('accessToken', accessToken.value);

        scheduleTokenRefresh(parseInt(response.data.data.access_token_lifetime));
    }

    function logout() {
        clearTimeout(refreshTimer.value);

        accessToken.value = null;
        userInfo.value = null;

        localStorage.removeItem("accessToken");
        removeRefreshToken();
    }

    async function initUser() {
        accessToken.value = localStorage.getItem('accessToken');

        await loadUserInfo();
    }

    return {
        accessToken,
        userInfo,
        isLoggedIn,
        login,
        logout,
        refreshAccessToken,
        initUser,
    };
});
