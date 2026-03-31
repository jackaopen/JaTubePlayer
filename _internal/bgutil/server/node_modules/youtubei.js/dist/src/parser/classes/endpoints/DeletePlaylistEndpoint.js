import { YTNode } from '../../helpers.js';
const API_PATH = 'playlist/delete';
export default class DeletePlaylistEndpoint extends YTNode {
    static type = 'DeletePlaylistEndpoint';
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
        if (this.#data.playlistId)
            request.playlistId = this.#data.sourcePlaylistId;
        return request;
    }
}
//# sourceMappingURL=DeletePlaylistEndpoint.js.map