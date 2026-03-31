import { YTNode } from '../../helpers.js';
const API_PATH = 'subscription/unsubscribe';
export default class UnsubscribeEndpoint extends YTNode {
    static type = 'UnsubscribeEndpoint';
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
        if (this.#data.channelIds)
            request.channelIds = this.#data.channelIds;
        if (this.#data.siloName)
            request.siloName = this.#data.siloName;
        if (this.#data.params)
            request.params = this.#data.params;
        return request;
    }
}
//# sourceMappingURL=UnsubscribeEndpoint.js.map