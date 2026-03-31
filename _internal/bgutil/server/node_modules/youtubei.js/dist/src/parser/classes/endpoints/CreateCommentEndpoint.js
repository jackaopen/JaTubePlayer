import { YTNode } from '../../helpers.js';
const API_PATH = 'comment/create_comment';
export default class CreateCommentEndpoint extends YTNode {
    static type = 'CreateCommentEndpoint';
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
        if (this.#data.createCommentParams)
            request.createCommentParams = this.#data.createCommentParams;
        if (this.#data.commentText)
            request.commentText = this.#data.commentText;
        if (this.#data.attachedVideoId)
            request.videoAttachment = { videoId: this.#data.attachedVideoId };
        else if (this.#data.pollOptions)
            request.pollAttachment = { choices: this.#data.pollOptions };
        else if (this.#data.imageBlobId)
            request.imageAttachment = { encryptedBlobId: this.#data.imageBlobId };
        else if (this.#data.sharedPostId)
            request.sharedPostAttachment = { postId: this.#data.sharedPostId };
        if (this.#data.accessRestrictions && typeof this.#data.accessRestrictions === 'number') {
            const restriction = this.#data.accessRestrictions === 1 ? 'RESTRICTION_TYPE_EVERYONE' : 'RESTRICTION_TYPE_SPONSORS_ONLY';
            request.accessRestrictions = { restriction };
        }
        if (this.#data.botguardResponse)
            request.botguardResponse = this.#data.botguardResponse;
        return request;
    }
}
//# sourceMappingURL=CreateCommentEndpoint.js.map