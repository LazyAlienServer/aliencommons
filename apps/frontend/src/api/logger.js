import { api } from './axiosInstance'

function sendLogToServer(logsToSend) {
    return api.post('/log/collect/', {
        logs: logsToSend
    })
}

export {
    sendLogToServer,
}
