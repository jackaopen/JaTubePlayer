import { YTNode } from '../../helpers.js';
const API_PATH = 'comment/perform_comment_action';
export default class PerformCommentActionEndpoint extends YTNode {
    static type = 'PerformCommentActionEndpoint';
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
        if (this.#data.actions)
            request.actions = this.#data.actions;
        if (this.#data.action)
            request.actions = [this.#data.action];
        return request;
    }
}
//# sourceMappingURL=PerformCommentActionEndpoint.js.map