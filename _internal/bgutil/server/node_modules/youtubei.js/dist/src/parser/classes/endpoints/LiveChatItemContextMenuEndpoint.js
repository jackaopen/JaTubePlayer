import { YTNode } from '../../helpers.js';
const API_PATH = 'live_chat/get_item_context_menu';
export default class LiveChatItemContextMenuEndpoint extends YTNode {
    static type = 'LiveChatItemContextMenuEndpoint';
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
        if (this.#data.params)
            request.params = this.#data.params;
        return request;
    }
}
//# sourceMappingURL=LiveChatItemContextMenuEndpoint.js.map