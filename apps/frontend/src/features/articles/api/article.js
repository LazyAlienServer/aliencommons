import { api } from '@/api'


function getMySourceArticles(query = undefined) {
    return api.get(
        '/source_articles/',
        {
            withCredentials: true,
            params: query,
        },
    );
}

function getTheSourceArticle(id) {
    return api.get(`/source_articles/${id}/`, { withCredentials: true });
}

function createSourceArticle() {
    return api.post(`/source_articles/`)
}

function updateSourceArticle(id, title, content) {
    return api.patch(
        `/source_articles/${id}/`,
        {
            title: title,
            content: content,
        },
        { withCredentials: true },
    )
}

function submitArticle(id) {
    return api.post(
        `/source_articles/${id}/submit/`,
        {},
        { withCredentials: true }
    );
}

function withdrawArticle(id) {
    return api.post(
        `/source_articles/${id}/withdraw/`,
        {},
        { withCredentials: true }
    );
}

function approveArticle(id) {
    return api.post(
        `/source_articles/${id}/approve/`,
        {},
        { withCredentials: true }
    );
}

function rejectArticle(id) {
    return api.post(
        `/source_articles/${id}/reject/`,
        {},
        { withCredentials: true }
    );
}

function unpublishArticle(id) {
    return api.post(
        `/source_articles/${id}/unpublish/`,
        {},
        { withCredentials: true }
    );
}

function deleteArticle(id) {
    return api.post(
        `/source_articles/${id}/delete/`,
        {},
        { withCredentials: true }
    );
}

function uploadArticleImage(formData) {

    return api.post(
        `/source_articles/images/`,
        formData,
        {
            headers: { 'Content-Type': 'multipart/form-data' },
            withCredentials: true,
        }
    )
}

function getPendingArticles() {
    return api.get('/article_snapshots/pending_ones/', { withCredentials: true });
}

function getThePendingArticle(id) {
    return api.get(`/article_snapshots/${id}/`, { withCredentials: true });
}

function getPublishedArticles() {
    return api.get('/published_articles/');
}

function getThePublishedArticle(id) {
    return api.get(`/published_articles/${id}/`);
}

export {
    getMySourceArticles,
    getTheSourceArticle,
    createSourceArticle,
    updateSourceArticle,
    submitArticle,
    withdrawArticle,
    approveArticle,
    rejectArticle,
    unpublishArticle,
    deleteArticle,
    uploadArticleImage,
    getPendingArticles,
    getThePendingArticle,
    getPublishedArticles,
    getThePublishedArticle,
}
