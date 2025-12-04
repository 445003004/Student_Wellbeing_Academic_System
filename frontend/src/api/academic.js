import request from '../utils/request'

export function getCourses() {
    return request({
        url: '/academic/courses',
        method: 'get'
    })
}

export function getCourseAnalytics(courseId) {
    return request({
        url: `/academic/courses/${courseId}/dashboard`,
        method: 'get'
    })
}

export function getAcademicAlerts() {
    return request({
        url: '/academic/dashboard/alerts',
        method: 'get'
    })
}

export function getStudentDetails(studentNumber) {
    return request({
        url: `/academic/students/${studentNumber}/details`,
        method: 'get'
    })
}
