import axios from 'axios'
import { useUserStore } from "@/features/user/stores/useUserStore";
import { getRefreshToken } from '@/utils'

const api = axios.create({
    baseURL: `${import.meta.env.VITE_API_BASE_URL}/api/v1`,
    timeout: 10000,
})

// Do not call useUserStore() outside the interceptors
let isRefreshing = false
let refreshPromise = null
const subscribers = []

function onRefreshed() {
    subscribers.forEach(function (callback) {
        callback()
    });
    subscribers.length = 0;
}

function addSubscriber(callback) {
    subscribers.push(callback)
}

api.interceptors.request.use((config) => {
    const userStore = useUserStore();

    config.headers.Authorization = `Bearer ${userStore.accessToken}`;

    return config;
});

api.interceptors.response.use(
    function (response) {
        return response;
    },
    async function (error) {
        const userStore = useUserStore();
        const originalRequest = error.config || {};
        const status = error?.response?.status
        const refreshToken = getRefreshToken();

        // Only enter the refresh logic when the status is 401
        if (status !== 401) {
            return Promise.reject(error);
        }

        // if no refreshToken exist and has retried request, logout and throw error
        if ( !refreshToken || originalRequest._retry) {
            userStore.logout();
            return Promise.reject(error);
        }

        originalRequest._retry = true;

        // If a refresh process exists, put the new refresh request in the waiting queue
        if (isRefreshing && refreshPromise) {
            return new Promise((resolve, reject) => {
                // Add a callback function into the subscriber list
                addSubscriber(() => {
                    try {
                        resolve(api(originalRequest))
                    } catch (error) {
                        reject(error)
                    }
                })
            })
        }

        // The part that triggers a refresh process
        try {
            isRefreshing = true

            refreshPromise = userStore.refreshAccessToken()
            await refreshPromise
            console.log("Access token successfully refreshed!")

            onRefreshed()

            return api(originalRequest)

        } catch (refreshErr) {
            // If the refresh fails
            userStore.logout()
            return Promise.reject(refreshErr)

        } finally {
            isRefreshing = false
            refreshPromise = null
        }
    }
);


// for requests outside the user system
const apiBare = axios.create({
    baseURL: `${import.meta.env.VITE_API_BASE_URL}/api/v1`,
    timeout: 10000,
})

export { api, apiBare }
