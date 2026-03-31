import { YTNode } from '../../helpers.js';
import NavigationEndpoint from '../NavigationEndpoint.js';
export default class AddToPlaylistCommand extends YTNode {
    static type = 'AddToPlaylistCommand';
    open_miniplayer;
    video_id;
    list_type;
    endpoint;
    video_ids;
    constructor(data) {
        super();
        this.open_miniplayer = data.openMiniplayer;
        this.video_id = data.videoId;
        this.list_type = data.listType;
        this.endpoint = new NavigationEndpoint(data.onCreateListCommand);
        this.video_ids = data.videoIds;
    }
}
//# sourceMappingURL=AddToPlaylistCommand.js.map