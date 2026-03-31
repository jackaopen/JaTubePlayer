import { YTNode } from '../../helpers.js';
const API_PATH = 'reel/reel_item_watch';
export default class ReelWatchEndpoint extends YTNode {
    static type = 'ReelWatchEndpoint';
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
        if (this.#data.videoId) {
            request.playerRequest = {
                videoId: this.#data.videoId
            };
        }
        if (request.playerRequest) {
            if (this.#data.playerParams)
                request.playerRequest.params = this.#data.playerParams;
            if (this.#data.racyCheckOk)
                request.playerRequest.racyCheckOk = !!this.#data.racyCheckOk;
            if (this.#data.contentCheckOk)
                request.playerRequest.contentCheckOk = !!this.#data.contentCheckOk;
        }
        if (this.#data.params)
            request.params = this.#data.params;
        if (this.#data.inputType)
            request.inputType = this.#data.inputType;
        request.disablePlayerResponse = !!this.#data.disablePlayerResponse;
        return request;
    }
}
//# sourceMappingURL=ReelWatchEndpoint.js.map