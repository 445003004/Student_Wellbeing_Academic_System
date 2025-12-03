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
