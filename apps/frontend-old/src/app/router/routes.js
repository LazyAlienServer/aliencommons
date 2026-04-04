import * as views from "@/pages";


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
        component: () => import("@/pages/user/LoginView.vue"),
        meta: { title: 'Login' },
    },
    {
        path: '/logout',
        name: 'logout',
        component: () => import("@/pages/user/LogoutView.vue"),
        meta: { title: 'Logout' },
    },
    {
        path: '/register',
        name: 'register',
        component: () => import("@/pages/user/RegisterView.vue"),
        meta: { title: 'Register' },
    },
    {
        path: '/profile/:username',
        name: 'profile',
        component: () => import("@/pages/user/ProfileView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Profile',
        },
    },
    {
        path: '/cookie-policy',
        name: 'cookie',
        component: () => import("@/pages/static/CookiePolicyView.vue"),
        meta: { title: 'Cookie Policy' },
    },
    {
        path: '/profile/settings/appearance',
        name: 'appearance',
        component: () => import("@/pages/user/AppearanceSettingView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Appearance',
        },
    },
    {
        path: `/studio/my-articles`,
        name: 'my-articles',
        component: () => import("@/pages/articles/MyArticleListView.vue"),
        meta: {
            requiresAuth: true,
            title: 'My Articles',
        }
    },
    {
        path: `/studio/article/:id/edit/`,
        name: 'article-editor',
        component: () => import("@/pages/articles/SourceArticleEditorView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Article Editor',
            showPageHeader: true,
        }
    },
    {
        path: `/studio/article/:id/review/`,
        name: 'article-review',
        component: () => import("@/pages/articles/SourceArticleReviewView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Article Review',
            showPageHeader: true,
        }
    },
    {
        path: `/staff/pending-articles`,
        name: 'pending-articles',
        component: () => import("@/pages/articles/PendingArticleListView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Pending Articles',
        }
    },
    {
        path: `/staff/article/:id/moderate/`,
        name: 'article-moderation',
        component: () => import("@/pages/articles/PendingArticleModerationView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Article Moderation',
            showPageHeader: true,
        }
    },
    {
        path: `/published-articles/`,
        name: 'published-article-list',
        component: () => import("@/pages/articles/PublishedArticleListView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Published Articles',
        }
    },
    {
        path: `/articles/:id/`,
        name: 'article-detail',
        component: () => import("@/pages/articles/PublishedArticleDetailView.vue"),
        meta: {
            requiresAuth: true,
            title: 'Article Detail',
        }
    },
    {
        path: '/:pathMatch(.*)*',
        name: '404',
        component: () => import("@/pages/misc/NotFoundView.vue"),
        meta: {title: '404'},
    },
]

export default routes
