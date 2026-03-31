import { YTNode } from '../../helpers.js';
const LIKE_API_PATH = 'like/like';
const DISLIKE_API_PATH = 'like/dislike';
const REMOVE_LIKE_API_PATH = 'like/removelike';
export default class LikeEndpoint extends YTNode {
    static type = 'LikeEndpoint';
    #data;
    constructor(data) {
        super();
        this.#data = data;
    }
    getApiPath() {
        return this.#data.status === 'DISLIKE' ?
            DISLIKE_API_PATH : this.#data.status === 'INDIFFERENT' ?
            REMOVE_LIKE_API_PATH : LIKE_API_PATH;
    }
    buildRequest() {
        const request = {};
        if (this.#data.target)
            request.target = this.#data.target;
        const params = this.getParams();
        if (params)
            request.params = params;
        return request;
    }
    getParams() {
        switch (this.#data.status) {
            case 'LIKE':
                return this.#data.likeParams;
            case 'DISLIKE':
                return this.#data.dislikeParams;
            case 'INDIFFERENT':
                return this.#data.removeLikeParams;
            default:
                return undefined;
        }
    }
}
//# sourceMappingURL=LikeEndpoint.js.map