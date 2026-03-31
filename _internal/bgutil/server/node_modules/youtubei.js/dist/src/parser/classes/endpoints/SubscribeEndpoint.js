import { YTNode } from '../../helpers.js';
const API_PATH = 'subscription/subscribe';
export default class SubscribeEndpoint extends YTNode {
    static type = 'SubscribeEndpoint';
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
        if (this.#data.botguardResponse)
            request.botguardResponse = this.#data.botguardResponse;
        if (this.#data.feature)
            request.clientFeature = this.#data.feature;
        return request;
    }
}
//# sourceMappingURL=SubscribeEndpoint.js.map