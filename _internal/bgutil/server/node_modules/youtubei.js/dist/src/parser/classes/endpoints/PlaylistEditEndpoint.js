import { YTNode } from '../../helpers.js';
const API_PATH = 'browse/edit_playlist';
export default class PlaylistEditEndpoint extends YTNode {
    static type = 'PlaylistEditEndpoint';
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
        if (this.#data.playlistId)
            request.playlistId = this.#data.playlistId;
        if (this.#data.params)
            request.params = this.#data.params;
        return request;
    }
}
//# sourceMappingURL=PlaylistEditEndpoint.js.map