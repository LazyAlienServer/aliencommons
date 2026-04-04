import { defineStore } from 'pinia';
import { ref } from 'vue';

const useThemeStore = defineStore('theme', () => {
    const theme = ref('light');

    function applyTheme(mode) {
        theme.value = mode;
        document.documentElement.setAttribute('data-theme', mode);
        localStorage.setItem('theme', mode);
    }

    function toggleTheme() {
        applyTheme(theme.value === 'light' ? 'dark' : 'light');
    }

    function initTheme() {
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme === 'dark' || storedTheme === 'light') {
            applyTheme(storedTheme);
        } else {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            applyTheme(prefersDark ? 'dark' : 'light');
        }
    }

    return {
        theme,
        applyTheme,
        toggleTheme,
        initTheme,
    }
});

export { useThemeStore };