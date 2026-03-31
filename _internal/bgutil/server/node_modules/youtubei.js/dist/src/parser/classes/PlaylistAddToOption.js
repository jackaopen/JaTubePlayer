import { YTNode } from '../helpers.js';
import { Text } from '../misc.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class PlaylistAddToOption extends YTNode {
    static type = 'PlaylistAddToOption';
    add_to_playlist_service_endpoint;
    contains_selected_videos;
    playlist_id;
    privacy;
    privacy_icon;
    remove_from_playlist_service_endpoint;
    title;
    constructor(data) {
        super();
        this.add_to_playlist_service_endpoint = new NavigationEndpoint(data.addToPlaylistServiceEndpoint);
        this.contains_selected_videos = data.containsSelectedVideos;
        this.playlist_id = data.playlistId;
        this.privacy = data.privacy;
        this.privacy_icon = { icon_type: data.privacyIcon?.iconType || null };
        this.remove_from_playlist_service_endpoint = new NavigationEndpoint(data.removeFromPlaylistServiceEndpoint);
        this.title = new Text(data.title);
    }
}
//# sourceMappingURL=PlaylistAddToOption.js.map