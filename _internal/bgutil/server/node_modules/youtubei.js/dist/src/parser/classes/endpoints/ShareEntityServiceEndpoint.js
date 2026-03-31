import { YTNode } from '../../helpers.js';
const API_PATH = 'share/get_share_panel';
export default class ShareEntityServiceEndpoint extends YTNode {
    static type = 'ShareEntityServiceEndpoint';
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
        if (this.#data.serializedShareEntity)
            request.serializedSharedEntity = this.#data.serializedShareEntity;
        if (this.#data.clientParams)
            request.clientParams = this.#data.clientParams;
        return request;
    }
}
//# sourceMappingURL=ShareEntityServiceEndpoint.js.map