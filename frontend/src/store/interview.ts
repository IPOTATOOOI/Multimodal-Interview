import { defineStore } from 'pinia'

const storageKey = 'interview_session_state'

const readSessionState = () => {
  if (typeof sessionStorage === 'undefined') return {}

  try {
    const raw = sessionStorage.getItem(storageKey)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

const writeSessionState = (state) => {
  if (typeof sessionStorage === 'undefined') return

  try {
    sessionStorage.setItem(storageKey, JSON.stringify(state))
  } catch {
    // ignore storage failures
  }
}

const initialState = readSessionState()

export const useInterviewStore = defineStore('interview', {
  state: () => ({
    historyId: initialState.historyId ?? null,
    firstQuestion: initialState.firstQuestion ?? null,
    questionQaId: initialState.questionQaId ?? null,
    currentTopic: initialState.currentTopic ?? null,
    writtenTestQuestions: initialState.writtenTestQuestions ?? null,
  }),
  actions: {
    setHistoryId(id) {
      this.historyId = id
      writeSessionState({
        historyId: this.historyId,
        firstQuestion: this.firstQuestion,
        questionQaId: this.questionQaId,
        currentTopic: this.currentTopic,
        writtenTestQuestions: this.writtenTestQuestions,
      })
    },
    setInterviewStartData(data) {
      this.historyId = data.history_id
      this.firstQuestion = data.first_question
      this.questionQaId = data.question_qa_id
      this.currentTopic = data.current_topic
      this.writtenTestQuestions = data.written_test_questions ?? null
      writeSessionState({
        historyId: this.historyId,
        firstQuestion: this.firstQuestion,
        questionQaId: this.questionQaId,
        currentTopic: this.currentTopic,
        writtenTestQuestions: this.writtenTestQuestions,
      })
    },
    setQuestionQaId(id) {
      this.questionQaId = id
      writeSessionState({
        historyId: this.historyId,
        firstQuestion: this.firstQuestion,
        questionQaId: this.questionQaId,
        currentTopic: this.currentTopic,
        writtenTestQuestions: this.writtenTestQuestions,
      })
    },
  },
})
