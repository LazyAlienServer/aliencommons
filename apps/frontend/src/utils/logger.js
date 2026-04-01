import { sendLogToServer } from '@/api';
import { useUserStore } from "@/features/user/stores";


const LOG_LEVELS = ['debug', 'info', 'warn', 'error'];

const logQueue = [];

const FLUSH_INTERVAL = 5 * 1000  // logQueue sends to server per 5 seconds

function formatMessage(level, message, extra) {
    const timestamp = new Date().toISOString();

    return {
        level,
        message,
        extra,
        timestamp,
        page: window.location.pathname,
    };
}

function log(level, message, extra = {}) {
    if (!LOG_LEVELS.includes(level)) {
        throw new Error('Unknown log level: ' + level);
    }

    const userStore = useUserStore();
    const logEntry = formatMessage(level, message, {
        ...extra,
        userId: userStore?.userInfo?.id || null,
    });

    logQueue.push(logEntry);

    const levelColors = {
        debug: 'gray',
        info: 'blue',
        warn: 'yellow',
        error: 'red',
    };

    const css = `color: ${levelColors[level]}; font-weight: bold;`;

    console[level](
        `%c[${level.toUpperCase()}] ${logEntry.timestamp} (${logEntry.page})`,
        css,
        logEntry.message,
        logEntry.extra,
    );
}

async function flushLogs() {
    if (logQueue.length === 0) {
        return;
    }

    const logsToSend = [...logQueue];

    try {
        await sendLogToServer(logsToSend);

        logQueue.length = [];

    } catch (error) {
        console.error('[Logger] Failed to send logs', error);
    }
}

setInterval(flushLogs, FLUSH_INTERVAL);

export default {
    debug(message, extra) {
        log('debug', message, extra);
    },
    info(message, extra) {
        log('info', message, extra);
    },
    warn(message, extra) {
        log('warn', message, extra);
    },
    error(message, extra) {
        log('error', message, extra);
    },
};
