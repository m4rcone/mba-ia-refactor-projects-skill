const express = require('express');
const config = require('./config');

const Database = require('./database/connection');
const initDatabase = require('./database/init');

const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditLogModel = require('./models/auditLogModel');
const ReportModel = require('./models/reportModel');

const CheckoutController = require('./controllers/checkoutController');
const ReportController = require('./controllers/reportController');
const UserController = require('./controllers/userController');

const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');
const errorHandler = require('./middlewares/errorHandler');

async function bootstrap() {
    const db = new Database(config.db.file);
    await initDatabase(db);

    const userModel = new UserModel(db);
    const courseModel = new CourseModel(db);
    const enrollmentModel = new EnrollmentModel(db);
    const paymentModel = new PaymentModel(db);
    const auditLogModel = new AuditLogModel(db);
    const reportModel = new ReportModel(db);

    const checkoutController = new CheckoutController({
        db,
        userModel,
        courseModel,
        enrollmentModel,
        paymentModel,
        auditLogModel,
    });
    const reportController = new ReportController({ reportModel });
    const userController = new UserController({ db, userModel, enrollmentModel, paymentModel });

    const app = express();
    app.use(express.json());

    app.use('/api/checkout', checkoutRoutes(checkoutController));
    app.use('/api/admin', reportRoutes(reportController));
    app.use('/api/users', userRoutes(userController));

    app.use(errorHandler);

    app.listen(config.port, () => {
        console.log(`API rodando na porta ${config.port}...`);
    });
}

bootstrap().catch((err) => {
    console.error('Falha ao iniciar a aplicação', err);
    process.exit(1);
});
