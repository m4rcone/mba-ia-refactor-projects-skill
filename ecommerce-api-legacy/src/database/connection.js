const sqlite3 = require('sqlite3').verbose();

class Database {
    constructor(filename) {
        this.db = new sqlite3.Database(filename);
    }

    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.run(sql, params, function (err) {
                if (err) return reject(err);
                resolve(this);
            });
        });
    }

    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
        });
    }

    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
        });
    }

    exec(sql) {
        return new Promise((resolve, reject) => {
            this.db.exec(sql, (err) => (err ? reject(err) : resolve()));
        });
    }

    async transaction(work) {
        await this.exec('BEGIN');
        try {
            const result = await work();
            await this.exec('COMMIT');
            return result;
        } catch (err) {
            await this.exec('ROLLBACK');
            throw err;
        }
    }
}

module.exports = Database;
