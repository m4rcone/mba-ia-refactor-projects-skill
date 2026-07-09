const passwordService = require('../services/passwordService');
const { PaymentStatus, APPROVED_CARD_PREFIX } = require('../constants');
const { NotFoundError, PaymentDeniedError } = require('../middlewares/errors');

const DEFAULT_PASSWORD = '123456';

class CheckoutController {
    constructor({ db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel }) {
        this.db = db;
        this.userModel = userModel;
        this.courseModel = courseModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
        this.auditLogModel = auditLogModel;
    }

    async checkout({ name, email, password, courseId, card }) {
        const course = await this.courseModel.findActiveById(courseId);
        if (!course) throw new NotFoundError('Curso não encontrado');

        const status = this.resolvePaymentStatus(card);
        if (status === PaymentStatus.DENIED) throw new PaymentDeniedError('Pagamento recusado');

        const userId = await this.resolveUserId({ name, email, password });

        return this.db.transaction(async () => {
            const enrollmentId = await this.enrollmentModel.create({ userId, courseId });
            await this.paymentModel.create({ enrollmentId, amount: course.price, status });
            await this.auditLogModel.create(`Checkout curso ${courseId} por ${userId}`);
            return { msg: 'Sucesso', enrollment_id: enrollmentId };
        });
    }

    async resolveUserId({ name, email, password }) {
        const existing = await this.userModel.findByEmail(email);
        if (existing) return existing.id;

        const passwordHash = passwordService.hash(password || DEFAULT_PASSWORD);
        return this.userModel.create({ name, email, passwordHash });
    }

    resolvePaymentStatus(card) {
        return card.startsWith(APPROVED_CARD_PREFIX) ? PaymentStatus.PAID : PaymentStatus.DENIED;
    }
}

module.exports = CheckoutController;
