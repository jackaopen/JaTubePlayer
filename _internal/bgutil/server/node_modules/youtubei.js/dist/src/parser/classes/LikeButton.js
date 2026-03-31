import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class LikeButton extends YTNode {
    static type = 'LikeButton';
    target;
    like_status;
    likes_allowed;
    endpoints;
    constructor(data) {
        super();
        this.target = {
            video_id: data.target.videoId
        };
        this.like_status = data.likeStatus;
        this.likes_allowed = data.likesAllowed;
        if (Reflect.has(data, 'serviceEndpoints')) {
            this.endpoints = data.serviceEndpoints.map((endpoint) => new NavigationEndpoint(endpoint));
        }
    }
}
//# sourceMappingURL=LikeButton.js.map