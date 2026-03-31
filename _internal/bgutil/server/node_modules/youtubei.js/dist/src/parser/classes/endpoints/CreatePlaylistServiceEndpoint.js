import { YTNode } from '../../helpers.js';
const API_PATH = 'playlist/create';
export default class CreatePlaylistServiceEndpoint extends YTNode {
    static type = 'CreatePlaylistServiceEndpoint';
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
        if (this.#data.title)
            request.title = this.#data.title;
        if (this.#data.privacyStatus)
            request.privacyStatus = this.#data.privacyStatus;
        if (this.#data.description)
            request.description = this.#data.description;
        if (this.#data.videoIds)
            request.videoIds = this.#data.videoIds;
        if (this.#data.params)
            request.params = this.#data.params;
        if (this.#data.sourcePlaylistId)
            request.sourcePlaylistId = this.#data.sourcePlaylistId;
        return request;
    }
}
//# sourceMappingURL=CreatePlaylistServiceEndpoint.js.map