const PaymentStatus = Object.freeze({
    PAID: 'PAID',
    DENIED: 'DENIED',
});

const APPROVED_CARD_PREFIX = '4';

module.exports = { PaymentStatus, APPROVED_CARD_PREFIX };
