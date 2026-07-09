const express = require('express');

module.exports = function reportRoutes(reportController) {
    const router = express.Router();

    router.get('/financial-report', async (req, res, next) => {
        try {
            const report = await reportController.getFinancialReport();
            res.status(200).json(report);
        } catch (err) {
            next(err);
        }
    });

    return router;
};
