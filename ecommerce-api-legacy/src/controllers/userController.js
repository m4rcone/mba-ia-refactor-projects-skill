class UserController {
    constructor({ db, userModel, enrollmentModel, paymentModel }) {
        this.db = db;
        this.userModel = userModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
    }

    async deleteUser(id) {
        await this.db.transaction(async () => {
            await this.paymentModel.deleteByUserId(id);
            await this.enrollmentModel.deleteByUserId(id);
            await this.userModel.deleteById(id);
        });
        return { msg: 'Usuário removido' };
    }
}

module.exports = UserController;
