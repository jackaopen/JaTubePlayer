import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class AutomixPreviewVideo extends YTNode {
    static type = 'AutomixPreviewVideo';
    playlist_video;
    constructor(data) {
        super();
        if (data?.content?.automixPlaylistVideoRenderer?.navigationEndpoint) {
            this.playlist_video = {
                endpoint: new NavigationEndpoint(data.content.automixPlaylistVideoRenderer.navigationEndpoint)
            };
        }
    }
}
//# sourceMappingURL=AutomixPreviewVideo.js.map