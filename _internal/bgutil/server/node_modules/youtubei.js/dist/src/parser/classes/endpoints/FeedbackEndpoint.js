import { YTNode } from '../../helpers.js';
const API_PATH = 'feedback';
export default class FeedbackEndpoint extends YTNode {
    static type = 'FeedbackEndpoint';
    #data;
    constructor(data) {
        super();
        this.#data = data;
    }
    getApiPath() {
        return API_PATH;
    }
    buildRequest() {
        const request = {};
        if (this.#data.feedbackToken)
            request.feedbackTokens = [this.#data.feedbackToken];
        if (this.#data.cpn)
            request.feedbackContext = { cpn: this.#data.cpn };
        request.isFeedbackTokenUnencrypted = !!this.#data.isFeedbackTokenUnencrypted;
        request.shouldMerge = !!this.#data.shouldMerge;
        return request;
    }
}
//# sourceMappingURL=FeedbackEndpoint.js.map