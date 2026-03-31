import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import DropdownView from './DropdownView.js';
import TextFieldView from './TextFieldView.js';
export default class CreatePlaylistDialogFormView extends YTNode {
    static type = 'CreatePlaylistDialogFormView';
    playlist_title;
    playlist_visibility;
    disable_playlist_collaborate;
    create_playlist_params_collaboration_enabled;
    create_playlist_params_collaboration_disabled;
    video_ids;
    constructor(data) {
        super();
        this.playlist_title = Parser.parseItem(data.playlistTitle, TextFieldView);
        this.playlist_visibility = Parser.parseItem(data.playlistVisibility, DropdownView);
        this.disable_playlist_collaborate = !!data.disablePlaylistCollaborate;
        this.create_playlist_params_collaboration_enabled = data.createPlaylistParamsCollaborationEnabled;
        this.create_playlist_params_collaboration_disabled = data.createPlaylistParamsCollaborationDisabled;
        this.video_ids = data.videoIds;
    }
}
//# sourceMappingURL=CreatePlaylistDialogFormView.js.map