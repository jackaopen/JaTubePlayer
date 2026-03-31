import { YTNode } from '../../helpers.js';
const API_PATH = 'notification/modify_channel_preference';
export default class ModifyChannelNotificationPreferenceEndpoint extends YTNode {
    static type = 'ModifyChannelNotificationPreferenceEndpoint';
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
        if (this.#data.secondaryParams)
            request.secondaryParams = this.#data.secondaryParams;
        return request;
    }
}
//# sourceMappingURL=ModifyChannelNotificationPreferenceEndpoint.js.map