import { YTNode } from '../../helpers.js';
const API_PATH = 'playlist/get_add_to_playlist';
export default class AddToPlaylistServiceEndpoint extends YTNode {
    static type = 'AddToPlaylistServiceEndpoint';
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
        request.videoIds = this.#data.videoIds ? this.#data.videoIds : [this.#data.videoId];
        if (this.#data.playlistId)
            request.playlistId = this.#data.playlistId;
        if (this.#data.params)
            request.params = this.#data.params;
        request.excludeWatchLater = !!this.#data.excludeWatchLater;
        return request;
    }
}
//# sourceMappingURL=AddToPlaylistServiceEndpoint.js.map