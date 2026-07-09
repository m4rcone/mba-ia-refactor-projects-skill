const express = require('express');
const { ValidationError } = require('../middlewares/errors');

module.exports = function checkoutRoutes(checkoutController) {
    const router = express.Router();

    router.post('/', async (req, res, next) => {
        try {
            const { usr, eml, pwd, c_id, card } = req.body;
            if (!usr || !eml || !c_id || !card) {
                throw new ValidationError('Bad Request');
            }

            const result = await checkoutController.checkout({
                name: usr,
                email: eml,
                password: pwd,
                courseId: c_id,
                card,
            });
            res.status(200).json(result);
        } catch (err) {
            next(err);
        }
    });

    return router;
};
