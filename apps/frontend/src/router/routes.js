import * as views from "@/views";


const routes = [
    {
        path: '/',
        name: 'home',
        component: views.HomeView,
        meta: { title: 'Home' },
    },
    {
        path: '/login',
        name: 'login',
        component: () => import("@/views/user/LoginView.vue"),
        meta: { title: 'Login' },
    },
    {
        path: '/logout',
        name: 'logout',
        component: () => import("@/views/user/LogoutView.vue"),
        meta: { title: 'Logout' },
    },
    {
        path: '/register',
        name: 'register',
        component: () => import("@/views/user/RegisterView.vue"),
        meta: { title: 'Register' },
    },
    {
        path: '/profile/:username',
        name: 'profile',
        component: () => import("@/views/user/ProfileView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Profile',
        },
    },
    {
        path: '/cookie-policy',
        name: 'cookie',
        component: () => import("@/views/static/CookiePolicyView.vue"),
        meta: { title: 'Cookie Policy' },
    },
    {
        path: '/profile/settings/appearance',
        name: 'appearance',
        component: () => import("@/views/user/AppearanceSettingView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Appearance',
        },
    },
    {
        path: `/studio/my-articles`,
        name: 'my-articles',
        component: () => import("@/views/articles/MyArticleListView.vue"),
        meta: {
            requiresAuth: true,
            title: 'My Articles',
        }
    },
    {
        path: `/studio/article/:id/edit/`,
        name: 'article-editor',
        component: () => import("@/views/articles/SourceArticleEditorView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Article Editor',
            showPageHeader: true,
        }
    },
    {
        path: `/studio/article/:id/review/`,
        name: 'article-review',
        component: () => import("@/views/articles/SourceArticleReviewView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Article Review',
            showPageHeader: true,
        }
    },
    {
        path: `/staff/pending-articles`,
        name: 'pending-articles',
        component: () => import("@/views/articles/PendingArticleListView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Pending Articles',
        }
    },
    {
        path: `/staff/article/:id/moderate/`,
        name: 'article-moderation',
        component: () => import("@/views/articles/PendingArticleModerationView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Article Moderation',
            showPageHeader: true,
        }
    },
    {
        path: `/published-articles/`,
        name: 'published-article-list',
        component: () => import("@/views/articles/PublishedArticleListView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Published Articles',
        }
    },
    {
        path: `/articles/:id/`,
        name: 'article-detail',
        component: () => import("@/views/articles/PublishedArticleDetailView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Article Detail',
        }
    },
    {
        path: '/:pathMatch(.*)*',
        name: '404',
        component: () => import("@/views/misc/NotFoundView.vue"),
        meta: {title: '404'},
    },
]

export default routes
