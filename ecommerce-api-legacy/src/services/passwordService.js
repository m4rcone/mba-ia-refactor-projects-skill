const crypto = require('crypto');

const KEY_LENGTH = 64;
const SALT_BYTES = 16;

function hash(password) {
    const salt = crypto.randomBytes(SALT_BYTES).toString('hex');
    const derivedKey = crypto.scryptSync(password, salt, KEY_LENGTH).toString('hex');
    return `${salt}:${derivedKey}`;
}

function verify(password, stored) {
    const [salt, key] = String(stored).split(':');
    if (!salt || !key) return false;

    const derivedKey = crypto.scryptSync(password, salt, KEY_LENGTH).toString('hex');
    return crypto.timingSafeEqual(Buffer.from(key, 'hex'), Buffer.from(derivedKey, 'hex'));
}

module.exports = { hash, verify };
