import { YTNode } from '../../helpers.js';
const API_PATH = 'next';
export default class WatchNextEndpoint extends YTNode {
    static type = 'WatchNextEndpoint';
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
        if (this.#data.videoId)
            request.videoId = this.#data.videoId;
        if (this.#data.playlistId)
            request.playlistId = this.#data.playlistId;
        if (this.#data.index !== undefined || this.#data.playlistIndex !== undefined)
            request.playlistIndex = this.#data.index || this.#data.playlistIndex;
        if (this.#data.playerParams || this.#data.params)
            request.params = this.#data.playerParams || this.#data.params;
        request.racyCheckOk = !!this.#data.racyCheckOk;
        request.contentCheckOk = !!this.#data.contentCheckOk;
        return request;
    }
}
//# sourceMappingURL=WatchNextEndpoint.js.map