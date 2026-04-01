import logger from "./logger";

function extractErrorMessage(err) {
    // axios backend response
    if (err?.response?.data?.detail) {
        return err.response.data.data.detail;
    }

    // axios response
    if (err?.response?.data) {
        return JSON.stringify(err.response.data.data);
    }

    // JS errors
    if (err?.message) {
        return err.message;
    }

    // last resort
    return String(err);
}

function setupGlobalErrorHandler(app) {
    app.config.errorHandler = function (error, instance, info) {
        const error_msg = extractErrorMessage(error);
        logger.error( 'Vue level error', {
            error: error_msg,
            info: info,
            component: instance?.$options?.name || 'anonymous',
        });
    };

    // global JS errors
    window.onerror = function (message, source, lineno, colno, error) {
        logger.error('Window error', {
            message: message,
            error: extractErrorMessage(error),
            source: source,  // "error at file" url
            lineno: lineno,  // Line No.
            colno: colno,  // Column No.
        });
    };

    // unhandled Promise exceptions
    window.onunhandledrejection = function (event) {
        logger.error('Unhandled Promise rejection', {
            error: extractErrorMessage(event.reason),  // event.reason = error message
        });
    };
}


export {
    extractErrorMessage,
    setupGlobalErrorHandler,
}
