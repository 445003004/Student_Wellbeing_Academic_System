import request from '../utils/request'

export function getWellbeingTrends() {
    return request({
        url: '/wellbeing/dashboard/trends',
        method: 'get'
    })
}

export function getRiskAlerts() {
    return request({
        url: '/wellbeing/dashboard/alerts',
        method: 'get'
    })
}

export function createSurvey(data) {
    return request({
        url: '/wellbeing/surveys',
        method: 'post',
        data
    })
}

export function getStudentHistory(studentNumber) {
    return request({
        url: `/wellbeing/students/${studentNumber}/history`,
        method: 'get'
    })
}

export function uploadCsvSurveys(formData) {
    return request({
        url: '/wellbeing/upload_csv',
        method: 'post',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data' // 必须指定，用于文件上传
        }
    })
}
