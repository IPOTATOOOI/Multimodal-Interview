import axios from 'axios';
import { API_BASE_URL } from '@/config/api';

export default {
  // 简历主记录
  createResume() {
    return axios.post(`${API_BASE_URL}/api/resumes`);
  },

  // 基本信息
  saveBasicInfo(data) {
    return axios.post(`${API_BASE_URL}/api/basic_info`, data);
  },

  // 教育背景
  saveEducation(data) {
    return axios.post(`${API_BASE_URL}/api/education`, data);
  },

  // 在校经历
  saveCampusExperience(data) {
    return axios.post(`${API_BASE_URL}/api/campus_experience`, data);
  },

  // 工作经历
  saveWorkExperience(data) {
    return axios.post(`${API_BASE_URL}/api/work_experience`, data);
  },

  // 项目经历
  saveProjectExperience(data) {
    return axios.post(`${API_BASE_URL}/api/project_experience`, data);
  },

  // 技能
  saveSkills(data) {
    return axios.post(`${API_BASE_URL}/api/skills`, data);
  },

  // 论文
  savePublications(data) {
    return axios.post(`${API_BASE_URL}/api/publications`, data);
  },

  // 求职意向
  saveJobIntention(data) {
    return axios.post(`${API_BASE_URL}/api/job_intention`, data);
  },

  // 竞赛经历
  saveCompetitionExperience(data) {
    return axios.post(`${API_BASE_URL}/api/competition_experience`, data);
  },

  // 证书
  saveCertificates(data) {
    return axios.post(`${API_BASE_URL}/api/certificates`, data);
  }
};