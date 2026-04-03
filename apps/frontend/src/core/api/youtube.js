import { apiBare } from './axiosInstance'

function getChannelSnapshot() {
    return apiBare.get('/pages/youtube_channel_snapshot/', {})
}

export {
    getChannelSnapshot,
}
