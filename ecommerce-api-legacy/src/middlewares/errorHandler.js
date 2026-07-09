module.exports = function errorHandler(err, req, res, next) {
    const status = err.status || 500;

    if (status >= 500) {
        console.error(err);
    }

    res.status(status).json({
        error: status >= 500 ? 'Internal server error' : err.message,
    });
};
