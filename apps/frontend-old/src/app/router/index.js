import {
    createRouter,
    createWebHistory,
} from 'vue-router'
import routes from './routes'
import { globalBeforeEach } from './guards';


const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach(globalBeforeEach)

export default router
