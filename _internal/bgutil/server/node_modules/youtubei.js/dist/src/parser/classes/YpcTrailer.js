import { YTNode } from '../helpers.js';
export default class YpcTrailer extends YTNode {
    static type = 'YpcTrailer';
    video_message;
    player_response;
    constructor(data) {
        super();
        this.video_message = data.fullVideoMessage;
        this.player_response = data.unserializedPlayerResponse;
    }
}
//# sourceMappingURL=YpcTrailer.js.map