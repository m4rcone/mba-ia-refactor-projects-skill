const express = require('express');
const { ValidationError } = require('../middlewares/errors');

module.exports = function userRoutes(userController) {
    const router = express.Router();

    router.delete('/:id', async (req, res, next) => {
        try {
            const id = Number(req.params.id);
            if (!Number.isInteger(id) || id <= 0) {
                throw new ValidationError('id inválido');
            }

            const result = await userController.deleteUser(id);
            res.status(200).json(result);
        } catch (err) {
            next(err);
        }
    });

    return router;
};
