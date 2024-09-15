// chatStore.js
let instance = null;

class ChatStore {
  constructor() {
    if (instance) {
      return instance;
    }
    this.currentChatId = null;
    instance = this;
  }

  setCurrentChatId(id) {
    this.currentChatId = id;
  }

  getCurrentChatId() {
    return this.currentChatId;
  }
}

const chatStore = Object.freeze(new ChatStore());
export default chatStore;