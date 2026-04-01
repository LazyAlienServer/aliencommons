import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import * as path from "node:path";
import removeConsole from "vite-plugin-remove-console";
import svgLoader from "vite-svg-loader";

export default defineConfig({
    plugins: [
        vue(),
        removeConsole({
            external: ['warn', 'error'],
        }),
        svgLoader(),
    ],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, 'src'),
        }
    },
    server: {
        host: '0.0.0.0',
        port: 5173,
        open: true,
        proxy: {
            '/api/v1': {
                target: 'http://backend:8000',
                changeOrigin: true,
                rewrite: path => path.replace(/^\/api\/v1/, '/api/v1'),
            },
        }
    },
    build: {
        sourcemap: false,
        target: 'esnext',
        outDir: 'dist',
        assetsDir: 'static',
    },
})
