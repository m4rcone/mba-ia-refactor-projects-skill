const { PaymentStatus } = require('../constants');

class ReportController {
    constructor({ reportModel }) {
        this.reportModel = reportModel;
    }

    async getFinancialReport() {
        const rows = await this.reportModel.getCourseFinancials();
        const byCourse = new Map();

        for (const row of rows) {
            if (!byCourse.has(row.course_id)) {
                byCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
            }

            if (row.enrollment_id == null) continue;

            const courseData = byCourse.get(row.course_id);
            if (row.payment_status === PaymentStatus.PAID) {
                courseData.revenue += row.payment_amount;
            }
            courseData.students.push({
                student: row.user_name || 'Unknown',
                paid: row.payment_amount != null ? row.payment_amount : 0,
            });
        }

        return Array.from(byCourse.values());
    }
}

module.exports = ReportController;
