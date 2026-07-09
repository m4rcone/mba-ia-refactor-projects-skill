module.exports = {
    port: Number(process.env.PORT) || 3000,
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
    db: {
        user: process.env.DB_USER || '',
        password: process.env.DB_PASSWORD || '',
        file: process.env.DB_FILE || ':memory:',
    },
};
