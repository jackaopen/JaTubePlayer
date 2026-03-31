import { YTNode } from '../helpers.js';
export default class MusicDownloadStateBadge extends YTNode {
    static type = 'MusicDownloadStateBadge';
    playlist_id;
    supported_download_states;
    constructor(data) {
        super();
        this.playlist_id = data.playlistId;
        this.supported_download_states = data.supportedDownloadStates;
    }
}
//# sourceMappingURL=MusicDownloadStateBadge.js.map